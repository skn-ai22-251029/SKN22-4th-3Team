import logging

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command

from src.core.config import LLMConfig
from src.core.fallbacks import FALLBACK_LLM, FALLBACK_SEARCH
from src.core.prompts.prompt_manager import prompt_manager
from src.retrieval.hybrid_search import HybridRetriever
from src.core.models.user import UserDTO
from src.core.models.matchmaker import BreedSelection, SearchIntent
from src.agents.filters.breed_criteria import extract_breed_criteria
from .state import AgentState

logger = logging.getLogger(__name__)

llm_router = init_chat_model(LLMConfig.ROUTER_MODEL, model_provider="openai", temperature=0)
llm_basic = init_chat_model(LLMConfig.BASIC_MODEL, model_provider="openai", temperature=0)

async def matchmaker_node(state: AgentState) -> Command:
    """
    매치메이커: 고양이 품종 추천 전문가.
    1. 검색 의도 분류 (LOOKUP vs RECOMMEND)
    2. 동적 쿼리 생성 및 검색
    3. 에이전틱 선별 (Top 3)
    """
    try:
      return await _matchmaker_node(state)
    except Exception:
        logger.exception("matchmaker_node 오류 발생")
        return Command(
            update={"messages": [AIMessage(content=FALLBACK_SEARCH)]},
            goto="__end__"
        )


async def _matchmaker_node(state: AgentState) -> Command:
    query = state["messages"][-1].content
    
    # UserDTO 초기화
    user = UserDTO.from_state(state)
        
    context = user.to_context_string()
    persona = prompt_manager.get_prompt("matchmaker", field="persona")

    # 1. 검색 의도 분류 (Intent Classification)
    intent_classifier = llm_router.with_structured_output(SearchIntent)
    intent = await intent_classifier.ainvoke([
        SystemMessage(content=(
            "당신은 고양이 전문가입니다. 사용자의 질문을 분석하여 검색 의도를 분류하세요.\n"
            "- LOOKUP: 특정 품종에 대한 정보나 특징을 묻는 경우 (프로필 무시)\n"
            "- RECOMMEND: 추천을 요청하는 경우 (사용자 환경 프로필 반영 필요)"
        )),
        SystemMessage(content=query)
    ], config={"tags": ["router_classification"]})

    # 2. 검색 쿼리 구성 및 조건 추출
    if intent.category == "RECOMMEND":
        # 추천: 프로필 적극 반영 + 선호 조건 추출 (Hard filter + fallback)
        search_query = f"{intent.keywords} (집사 환경: {context})"
        specialist_mode = "Matchmaker (Recommendation)"
        filter_result = await extract_breed_criteria(query)
    else:
        # 단순 조회: 프로필 배제
        search_query = intent.keywords
        specialist_mode = "Matchmaker (Lookup)"
        filter_result = None
        
    print(f"🕵️ [MATCHMAKER] Intent: {intent.category}, Query: {search_query}")

    # 3. 10건 후보 검색
    search_filters = {"categories": "Breeds"}
    if filter_result and filter_result.mongo_filter:
        search_filters.update(filter_result.mongo_filter)

    # RECOMMEND 모드: user_profile hard constraints 적용 (안전 필수 제약, LLM 우회 불가)
    # allergy, has_children, has_dog, has_cat, work_style 기반 MongoDB 필터를 강제 적용
    if intent.category == "RECOMMEND":
        hard_constraints = user.get_hard_constraints()
        for k, v in hard_constraints.items():
            search_filters[f"stats.{k}"] = v

    retriever = HybridRetriever(collection_name="care_guides")
    raw_results = await retriever.search(
        search_query,
        specialist="Matchmaker",
        filters=search_filters,
        limit=10
    )

    if not raw_results:
        return Command(update={"specialist_result": {"source": "matchmaker", "rag_docs": []}}, goto="head_butler")

    # 4. 에이전틱 랭킹: LLM이 10건 중 최적 3건 선별
    selection_prompt = f"""당신은 고양이 전문 매치메이커입니다. 
아래의 [사용자 환경]과 [질문]을 바탕으로, 10개의 [후보 리스트] 중에서 가장 적합한 3마리를 선정하세요.

[사용자 환경]
{context if intent.category == "RECOMMEND" else "(단순 조회이므로 환경 무시)"}

[질문]
{query}

[선정 원칙]
1. 단순 조회(LOOKUP)일 경우 질문한 품종을 최우선으로 찾으세요. **만약 후보 리스트에 질문한 품종이 명확히 없다면, 억지로 비슷한 것을 선택하지 말고 빈 리스트([])를 반환하세요.**
2. 추천(RECOMMEND)일 경우 알레르기/거주환경을 엄격히 고려하세요.

[후보 리스트]
"""
    for i, r in enumerate(raw_results):
        selection_prompt += f"{i}. {r.get('name_ko')} ({r.get('name_en')}): {r.get('summary')}\n"
        selection_prompt += f"   - 특징: {', '.join(r.get('personality_traits', []))}\n\n"

    if filter_result and filter_result.applied_conditions:
        conditions_str = ", ".join(filter_result.applied_conditions)
        selection_prompt += f"\n[적용된 검색 조건]\n{conditions_str}\n"
        if filter_result.fallback_applied:
            selection_prompt += f"※ {filter_result.fallback_reason}\n"
        selection_prompt += "위 조건이 반영된 후보 목록입니다. 사용자 환경과 종합하여 최적의 3종을 선별하세요.\n"

    selector = llm_router.with_structured_output(BreedSelection)
    selection = await selector.ainvoke(
        [SystemMessage(content=selection_prompt)],
        config={"tags": ["router_classification"]}
    )
    
    # 5. 상위 3건 필터링
    final_indices = selection.selected_indices[:3]
    top_results = [raw_results[i] for i in final_indices if i < len(raw_results)]

    # 품종을 못 찾은 경우 (Empty Selection)
    if not top_results and intent.category == "LOOKUP":
        print(f"🕵️ [MATCHMAKER] Unknown breed requested: {query}")
        return Command(
            update={
                "specialist_result": {
                    "source": "matchmaker",
                    "type": "breed_recommendation",
                    "specialist_name": "매치메이커 비서",
                    "persona": persona, 
                    "user_context": context,
                    "rag_context": "검색 결과에 해당 품종이 존재하지 않습니다.", # Head Butler가 이를 인지하고 CASE 3("모른다냥")로 대응하도록 유도
                    "rag_docs": []
                },
                "recommendations": [],
                "rag_docs": [],
            },
            goto="head_butler"
        )

    # 선별된 품종 정보를 집사용으로 압축
    rag_context = ""
    if top_results:
        docs_block = "\n\n".join([
            f"[{r.get('name_ko', '')} ({r.get('name_en', '')})]\n{r.get('text', '')[:1500]}"
            for r in top_results
        ])
        distill_msg = await llm_basic.ainvoke([
            SystemMessage(content=(
                "아래 추천 품종 정보에서 사용자에게 설명할 핵심 특징만 간결하게 추출하세요.\n"
                "- 품종별 2~3줄, 성격/생활환경 적합성/주의사항 위주\n"
                "- 총 400자 이내\n\n"
                f"[사용자 질문]\n{query}\n\n"
                f"[추천 품종 정보]\n{docs_block}"
            ))
        ], config={"tags": ["router_classification"]})
        rag_context = distill_msg.content

    # UI DTO 가공
    results = []
    for r in top_results:
        clean_r = {k: (str(v) if k == "_id" else v) for k, v in r.items()}
        if "tags" not in clean_r:
            traits = clean_r.get("personality_traits", [])
            clean_r["tags"] = [f"#{t}" for t in traits[:4]] if traits else []
        results.append(clean_r)

    # 선별된 top_results 기준으로만 rag_docs 생성 (raw_results 전체 X)
    # → head_butler LLM이 10개가 아닌 3개 품종 이름만 보게 되어 답변 일관성 확보
    rag_docs = [
        {
            "title": r.get("name_ko", ""),
            "subtitle": r.get("name_en", ""),
            "source": "TheCatAPI, Wikipedia",
            "url": r.get("source_url") or r.get("source_urls", [""])[0] if r.get("source_urls") else "",
        }
        for r in top_results
    ]

    reasoning_text = f"**[{intent.category}]** 모드로 검색했습니다.\n\n[선별 이유]\n{selection.reasoning}"

    specialist_result = {
        "source": "matchmaker",
        "type": "breed_recommendation",
        "specialist_name": "매치메이커 비서",
        "persona": persona + f"\n\n{reasoning_text}",
        "user_context": context,
        "rag_context": rag_context,
        "rag_docs": rag_docs,
    }

    return Command(
        update={
            "specialist_result": specialist_result,
            "recommendations": results,
            "rag_docs": rag_docs,
        },
        goto="head_butler"
    )
