"""
케어팀: 건강 및 행동 상담 전문가
"""
from typing import Literal

from langchain.chat_models import init_chat_model
from src.core.config import LLMConfig
from langchain_core.messages import SystemMessage
from langgraph.types import Command
from pydantic import BaseModel, Field

from .state import AgentState
from src.core.prompts.prompt_manager import prompt_manager
from src.retrieval.hybrid_search import HybridRetriever

llm_router = init_chat_model(LLMConfig.ROUTER_MODEL, model_provider="openai")
llm_basic = init_chat_model(LLMConfig.BASIC_MODEL, model_provider="openai")


class CareClassification(BaseModel):
    """케어팀 내부 분류 모델"""
    category: Literal["physician", "peacekeeper"] = Field(
        description="분류: 건강/의료/식이/응급(physician), 행동/심리/합사(peacekeeper)"
    )
    reasoning: str = Field(description="분류 이유")


SPECIALIST_CONFIG = {
    "physician": {
        "name": "주치의 비서",
        "persona_key": "physician",
        "specialist_tag": "Physician",
    },
    "peacekeeper": {
        "name": "행동 전문 비서",
        "persona_key": "peacekeeper",
        "specialist_tag": "Peacekeeper",
    },
}


async def care_team_node(state: AgentState) -> Command:
    """
    케어팀: 건강 + 행동 상담 통합 노드.

    specialist_result에 구조화된 JSON을 반환 (AIMessage가 아님).
    집사가 최종 사용자 응답을 생성함.
    """

    last_msg = state["messages"][-1].content

    # 1. LLM 기반 분류
    classifier = llm_router.with_structured_output(CareClassification)
    decision = await classifier.ainvoke([
        SystemMessage(content=(
            "사용자의 고양이 관련 질문을 분류하세요.\n"
            "- physician: 질병, 응급, 약물, 영양/식이, 생물학적 팩트, 의료적 오해, 위험한 처치\n"
            "- peacekeeper: 행동, 심리, 합사, 순화, 구조/포획, 훈련"
        )),
        *state["messages"]
    ], config={"tags": ["router_classification"]})

    config = SPECIALIST_CONFIG[decision.category]

    # 2. 페르소나 프롬프트 로딩
    persona = prompt_manager.get_prompt(config["persona_key"], field="persona")

    # 3. 전문가 태그 기반 RAG 검색
    retriever = HybridRetriever(version="v3", collection_name="care_guides")
    results = await retriever.search(
        last_msg, specialist=config["specialist_tag"], limit=3
    )

    # 4. RAG 컨텍스트 압축 — LLM이 원문에서 핵심 정보 추출
    rag_context = ""
    if results:
        docs_block = "\n\n".join([
            f"[{r.get('title_refined', '') or r.get('title', '')}]\n{r.get('text', '')[:1500]}"
            for r in results
        ])
        distill_msg = await llm_basic.ainvoke([
            SystemMessage(content=(
                "아래 참고 문서들에서 사용자 질문에 답하는 데 필요한 핵심 정보만 간결하게 추출하세요.\n"
                "- 불필요한 서론/반복 제거, 핵심 팩트와 수치 위주로 정리\n"
                "- 3~5개 bullet point, 총 300자 이내\n\n"
                f"[사용자 질문]\n{last_msg}\n\n"
                f"[참고 문서]\n{docs_block}"
            ))
        ], config={"tags": ["router_classification"]})
        rag_context = distill_msg.content

    # 5. 집사에게 전달할 구조화된 결과 생성
    rag_docs = [
        {
            "title": r.get("title_refined", "") or r.get("title", ""),
            "subtitle": r.get("specialist_tag", ""),
            "source": r.get("source", "건강 가이드"),
            "url": r.get("source_url") or r.get("source_urls", [""])[0] if r.get("source_urls") else "",
        }
        for r in results
    ]

    specialist_result = {
        "source": "care_team",
        "sub_specialist": decision.category,
        "specialist_name": config["name"],
        "reasoning": decision.reasoning,
        "persona": persona,
        "rag_context": rag_context,
        "rag_docs": rag_docs,
    }

    return Command(
        update={
            "specialist_result": specialist_result,
            "rag_docs": rag_docs,
        },
        goto="head_butler"
    )
