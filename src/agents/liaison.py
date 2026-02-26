"""
리에종: 입양 및 구조 정보 전문가
"""
from langchain.chat_models import init_chat_model
from src.core.config import LLMConfig
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.types import Command

from .state import AgentState
from .tools.animal_protection import search_abandoned_animals
from src.core.prompts.prompt_manager import prompt_manager
from src.retrieval.hybrid_search import HybridRetriever

llm_router = init_chat_model(LLMConfig.ROUTER_MODEL, model_provider="openai")
llm_basic = init_chat_model(LLMConfig.BASIC_MODEL, model_provider="openai")
llm_with_tools = llm_router.bind_tools([search_abandoned_animals])


async def liaison_node(state: AgentState) -> Command:
    """
    리에종: 입양/구조 정보 전문가.

    - RAG 검색 (specialist="Liaison", 입양/구조 관련 222건)
    - 도구 호출: 국가동물보호정보시스템 API (구조동물 조회)
    - specialist_result에 구조화된 JSON을 반환하여 집사에게 전달.
    """

    last_msg = state["messages"][-1]
    profile = state.get("user_profile", {})

    # 도구 실행 후 복귀 시, 도구 결과를 구조화된 출력으로 패키징
    if isinstance(last_msg, ToolMessage):
        tool_content = last_msg.content
        specialist_result = {
            "source": "liaison",
            "type": "tool_result",
            "specialist_name": "입양/구조 비서",
            "persona": prompt_manager.get_prompt("liaison", field="persona"),
            "tool_output": tool_content,
            "rag_docs": [],
        }
        return Command(
            update={"specialist_result": specialist_result},
            goto="head_butler"
        )

    query = last_msg.content
    context = f"거주: {profile.get('housing', '미설정')}, 활동량: {profile.get('activity', '미설정')}"

    # 1. 동물보호 조회 여부 판단 — LLM(도구 바인딩)이 직접 결정
    # 집사가 이미 입양 의도로 라우팅했으므로 LLM에 먼저 위임해도 안전함.
    ai_msg = await llm_with_tools.ainvoke(
        state["messages"],
        config={"tags": ["router_classification"]}
    )
    if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
        return Command(
            update={"messages": [ai_msg]},
            goto="tools"
        )

    # 2. 리에종 전문가 태그 기반 RAG 검색
    retriever = HybridRetriever(version="v3", collection_name="care_guides")
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
