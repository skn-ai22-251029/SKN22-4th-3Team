"""
수석 집사: 메인 라우터 및 응답 합성기
"""
import json
import logging

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from typing import Literal

from src.core.config import LLMConfig, TokenConfig
from src.core.fallbacks import FALLBACK_LLM
from src.core.prompts.prompt_manager import prompt_manager
from src.core.token_utils import trim_history
from .state import AgentState

logger = logging.getLogger(__name__)

llm_router = init_chat_model(LLMConfig.ROUTER_MODEL, model_provider="openai")
llm_basic = init_chat_model(
    LLMConfig.BASIC_MODEL,
    model_provider="openai",
    max_tokens=TokenConfig.MAX_TOKENS_PER_TURN,
)


class RouterDecision(BaseModel):
    """라우팅 분류 결과 모델"""
    category: Literal["matchmaker", "liaison", "care", "general"] = Field(
        description="Query classification: matchmaker (품종 추천/비교/매칭), liaison (입양 절차/구조동물/보호소), care (건강/행동 상담), general (인사/잡담)"
    )
    reasoning: str = Field(description="분류 근거")


POSTPROCESS_PROMPT = """당신은 ZIPSA의 수석 집사냥입니다.
전문가 팀이 조사한 결과를 바탕으로 사용자에게 최종 답변을 작성하세요.

[전문가 보고서]
{specialist_json}

[답변 규칙]
1. 전문가의 페르소나(persona)를 반영하여 해당 전문가의 톤으로 답변하세요.
2. **rag_context(핵심 요약)를 답변의 근거로 반드시 활용하세요.** rag_context가 비어 있으면 일반 지식으로 답변하세요.
3. rag_docs는 출처 표시용이므로 답변 본문에 인용하지 마세요.
4. rescue_cats 데이터가 있을 때: JSON을 그대로 출력하지 마세요. 마리 수와 간단한 분위기만 언급하고 ("N마리를 찾았어요!"), 상세 정보는 화면 카드에서 확인할 수 있다고 안내하세요.
   rescue_cats가 비어 있을 때: 해당 지역에 현재 보호 중인 고양이가 없음을 자연스럽게 안내하세요.
5. 답변 마지막에 구분선(---) 후 수석 집사로서 1~2문장 마무리 멘트를 덧붙이세요.
6. 마무리 멘트: 추가 질문 유도 또는 다른 전문가 연결 제안. 냥체(~다냥, ~하냥, ~냥) 사용.
"""


async def head_butler_node(state: AgentState) -> Command:
    """
    수석 집사: 그래프의 메인 라우터 겸 유일한 종료 지점.

    - 첫 방문: 질문 분류 → 전문가로 라우팅 또는 직접 응답 (general)
    - 재방문: specialist_result JSON 읽기 → 최종 AIMessage 생성 → END
    """
    try:
        specialist_result = state.get("specialist_result")

        # 재방문: 전문가가 구조화된 결과를 보고함
        if specialist_result and state.get("router_decision") in ("matchmaker", "liaison", "care"):
            # tool_output은 raw JSON이므로 LLM 프롬프트에서 제외
            specialist_for_prompt = {k: v for k, v in specialist_result.items() if k != "tool_output"}
            prompt = POSTPROCESS_PROMPT.format(
                specialist_json=json.dumps(specialist_for_prompt, ensure_ascii=False, indent=2)
            )
            history = trim_history(state["messages"], TokenConfig.MAX_HISTORY_TOKENS, llm_basic)
            response = await llm_basic.ainvoke([
                SystemMessage(content=prompt),
                *history,
            ])

            return Command(
                update={
                    "router_decision": None,
                    "specialist_result": None,
                    "messages": [response],
                },
                goto="__end__"
            )

        # 첫 방문: 분류 및 라우팅
        system_prompt = prompt_manager.get_prompt("head_butler")
        router = llm_router.with_structured_output(RouterDecision)
        history = trim_history(state["messages"], TokenConfig.MAX_HISTORY_TOKENS, llm_router)
        decision = await router.ainvoke(
            [SystemMessage(content=system_prompt)] + history,
            config={"tags": ["router_classification"]}
        )

        # 이전 턴의 잔여 결과 초기화
        updates: dict = {
            "router_decision": decision.category,
            "recommendations": [],
            "rag_docs": []
        }

        # 일반 질문은 직접 처리 → AIMessage → END
        if decision.category == "general":
            profile = state.get("user_profile", {})
            profile_context = f"거주: {profile.get('housing', '미설정')}, 활동량: {profile.get('activity', '미설정')}"

            general_prompt = prompt_manager.get_prompt("general")
            general_prompt = general_prompt.format(profile_context=profile_context)

            history = trim_history(state["messages"], TokenConfig.MAX_HISTORY_TOKENS, llm_basic)
            response = await llm_basic.ainvoke([
                SystemMessage(content=general_prompt),
                *history,
            ])

            updates.update({"messages": [response]})
            return Command(update=updates, goto="__end__")

        # 전문가로 라우팅
        return Command(update=updates, goto=decision.category)

    except Exception:
        logger.exception("head_butler_node 오류 발생")
        return Command(
            update={"messages": [AIMessage(content=FALLBACK_LLM)]},
            goto="__end__"
        )
