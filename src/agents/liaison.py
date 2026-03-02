"""
리에종: 입양 및 구조 정보 전문가
"""
import json
import logging

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langgraph.types import Command

from src.core.config import LLMConfig, TokenConfig
from src.core.fallbacks import FALLBACK_LLM, FALLBACK_TOOL
from src.core.token_utils import trim_history
from src.core.models.user import UserDTO
from src.core.prompts.prompt_manager import prompt_manager
from src.retrieval.hybrid_search import HybridRetriever
from .state import AgentState
from .tools.animal_protection import search_abandoned_animals

logger = logging.getLogger(__name__)

llm_router = init_chat_model(LLMConfig.ROUTER_MODEL, model_provider="openai")
llm_basic = init_chat_model(LLMConfig.BASIC_MODEL, model_provider="openai")
llm_with_tools = llm_router.bind_tools([search_abandoned_animals])


async def liaison_node(state: AgentState) -> Command:
    """
    리에종: 입양/구조 정보 전문가.
    """
    try:
        return await _liaison_node(state)
    except Exception:
        logger.exception("liaison_node 오류 발생")
        return Command(
            update={"messages": [AIMessage(content=FALLBACK_TOOL)]},
            goto="__end__"
        )


async def _liaison_node(state: AgentState) -> Command:
    """
    리에종 내부 구현.

    - RAG 검색 (specialist="Liaison", 입양/구조 관련 222건)
    - 도구 호출: 국가동물보호정보시스템 API (구조동물 조회)
    - specialist_result에 구조화된 JSON을 반환하여 집사에게 전달.
    """

    last_msg = state["messages"][-1]
    user = UserDTO.from_state(state)

    # 도구 실행 후 복귀 시, 도구 결과를 구조화된 출력으로 패키징
    if isinstance(last_msg, ToolMessage):
        tool_content = last_msg.content
        rescue_cats = []
        try:
            tool_data = json.loads(tool_content) if isinstance(tool_content, str) else tool_content
            rescue_cats = tool_data.get("rescue_cats", [])
        except (json.JSONDecodeError, AttributeError):
            logger.warning("ToolMessage content JSON 파싱 실패")

        specialist_result = {
            "source": "liaison",
            "type": "tool_result",
            "specialist_name": "입양/구조 비서",
            "persona": prompt_manager.get_prompt("liaison", field="persona"),
            "tool_output": tool_content,
            "rescue_cats": rescue_cats,
            "rag_docs": [],
        }
        return Command(
            update={"specialist_result": specialist_result, "rescue_cats": rescue_cats},
            goto="head_butler"
        )

    query = last_msg.content
    context = user.to_context_string()

    # 1. 동물보호 조회 여부 판단 — LLM(도구 바인딩)이 직접 결정
    # 집사가 이미 입양 의도로 라우팅했으므로 LLM에 먼저 위임해도 안전함.
    history = trim_history(state["messages"], TokenConfig.MAX_HISTORY_TOKENS, llm_router)
    ai_msg = await llm_with_tools.ainvoke(
        history,
        config={"tags": ["router_classification"]}
    )
    if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
        return Command(
            update={"messages": [ai_msg]},
            goto="tools"
        )

    # 2. 리에종 전문가 태그 기반 RAG 검색
    retriever = HybridRetriever(collection_name="care_guides")
    raw_results = await retriever.search(
        query, specialist="Liaison", limit=3
    )

    results = []
    for r in raw_results:
        clean_r = {k: (str(v) if k == "_id" else v) for k, v in r.items()}
        results.append(clean_r)

    # RAG 컨텍스트 압축 — 집사용 핵심 정보 추출
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
                f"[사용자 질문]\n{query}\n\n"
                f"[참고 문서]\n{docs_block}"
            ))
        ], config={"tags": ["router_classification"]})
        rag_context = distill_msg.content

    rag_docs = [
        {
            "title": r.get("title_refined", "") or r.get("title", ""),
            "subtitle": r.get("specialist_tag", ""),
            "source": r.get("source", "입양 가이드"),
            "url": r.get("source_url") or r.get("source_urls", [""])[0] if r.get("source_urls") else "",
        }
        for r in results
    ]

    persona = prompt_manager.get_prompt("liaison", field="persona")

    specialist_result = {
        "source": "liaison",
        "type": "adoption_info",
        "specialist_name": "입양/구조 비서",
        "persona": persona,
        "user_context": context,
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
