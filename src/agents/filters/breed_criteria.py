from pydantic import BaseModel, Field
from typing import List, Optional
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from src.core.config import LLMConfig, ZipsaConfig
from src.utils.mongodb import MongoDBManager

llm_router = init_chat_model(LLMConfig.ROUTER_MODEL, model_provider="openai", temperature=0)

# 실제 데이터 기반 threshold 정의 (67종 분포 기준)
# - affection_level (97%가 4-5), child_friendly (85%가 >=4), adaptability (평균 4.8): 분화 없음 → 제외
# - social_needs: 실제 min=3, "독립적인" 기준 <= 3 (energy_level <= 2는 4종뿐 → 미사용)
# - energy_level: "얌전한" 기준 <= 3 (>= 4: 61%, <= 3: 39%)
_SYSTEM_PROMPT = """사용자의 발화에서 고양이 품종 선호 조건을 추출하세요.

아래 필드와 척도를 사용합니다:
- shedding_level: 털 빠짐 (1-5, 높을수록 많이 빠짐)
- energy_level: 활동성 (1-5, 높을수록 활발)
- vocalisation: 울음소리 빈도 (1-5)
- grooming: 그루밍 필요도 (1-5)
- intelligence: 지능 (1-5, 높을수록 영리함)
- social_needs: 사회적 욕구 (3-5, 낮을수록 독립적)
- hypoallergenic: 저알레르기 (0 또는 1)
- lap: 무릎냥이 여부 (0 또는 1)

표현 → 조건 매핑:
- "털 안 빠지는", "털 적은" → shedding_level <= 2
- "활발한", "에너지 넘치는" → energy_level >= 4
- "얌전한", "조용한", "차분한" → energy_level <= 3
- "초보자", "처음 키우는", "입문용" → energy_level <= 3, grooming <= 3
- "소리 안 내는", "울음 적은" → vocalisation <= 2
- "혼자 있어도 괜찮은", "독립적인" → social_needs <= 3
- "알레르기" → hypoallergenic == 1
- "무릎냥이" → lap == 1
- "그루밍 적게", "관리 쉬운" → grooming <= 2
- "영리한", "훈련 가능한", "지능 높은" → intelligence >= 4

주의: energy_level <= 2는 데이터상 4종뿐이므로 사용하지 마세요. 최솟값은 <= 3입니다.
조건 형식: "shedding_level <= 2", "energy_level >= 4", "hypoallergenic == 1"
조건이 없으면 빈 리스트를 반환하세요."""

_BINARY_FIELDS = {"hypoallergenic", "lap", "indoor"}
_MIN_RESULT_COUNT = 3


class _ExtractedConditions(BaseModel):
    conditions: List[str] = Field(default_factory=list)


class FilterResult(BaseModel):
    """필터 적용 결과. matchmaker에서 RAG 검색 및 프롬프트 주입에 사용됩니다."""
    original_conditions: List[str] = Field(default_factory=list)
    applied_conditions: List[str] = Field(default_factory=list)
    mongo_filter: dict = Field(default_factory=dict)
    fallback_applied: bool = False
    fallback_reason: str = ""


def _parse_to_mongo(cond: str) -> tuple[Optional[str], object]:
    """조건 문자열을 MongoDB 필터 (path, value)로 변환합니다."""
    parts = cond.strip().split()
    if len(parts) != 3:
        return None, None
    field, op, value_str = parts
    try:
        value = int(value_str)
    except ValueError:
        return None, None
    path = f"stats.{field}"
    if op == "<=":
        return path, {"$lte": value}
    elif op == ">=":
        return path, {"$gte": value}
    elif op == "==":
        return path, value
    return None, None


def _conditions_to_mongo(conditions: List[str]) -> dict:
    result = {}
    for cond in conditions:
        path, value = _parse_to_mongo(cond)
        if path:
            result[path] = value
    return result


def _relax(cond: str) -> str:
    """수치 조건의 threshold를 ±1 완화합니다. 바이너리 조건은 그대로 반환합니다."""
    parts = cond.strip().split()
    if len(parts) != 3:
        return cond
    field, op, value_str = parts
    if field in _BINARY_FIELDS:
        return cond
    try:
        value = int(value_str)
    except ValueError:
        return cond
    if op == "<=":
        return f"{field} <= {value + 1}"
    elif op == ">=":
        return f"{field} >= {value - 1}"
    return cond


def _is_binary(cond: str) -> bool:
    return cond.strip().split()[0] in _BINARY_FIELDS


async def _count_breeds(collection, mongo_filter: dict) -> int:
    base = {"categories": "Breeds"}
    base.update(mongo_filter)
    return await collection.count_documents(base)


async def extract_breed_criteria(query: str) -> FilterResult:
    """
    사용자 발화에서 품종 필터 조건을 추출하고, 실제 데이터 기반 fallback을 적용합니다.

    Fallback 순서:
        1. 전체 조건 적용 → 결과 >= 3종이면 완료
        2. 수치 조건 threshold ±1 완화
        3. 바이너리 조건(hypoallergenic, lap)만 유지
        4. 조건 없음 (전체 검색)
    """
    extractor = llm_router.with_structured_output(_ExtractedConditions)
    extracted = await extractor.ainvoke(
        [SystemMessage(content=_SYSTEM_PROMPT), SystemMessage(content=query)],
        config={"tags": ["router_classification"]}
    )
    original = extracted.conditions

    if not original:
        return FilterResult()

    policy = ZipsaConfig.get_policy("v3")
    db = MongoDBManager.get_v3_db()
    collection = db[policy.collection_name]

    # 1단계: 전체 조건
    mongo_filter = _conditions_to_mongo(original)
    if await _count_breeds(collection, mongo_filter) >= _MIN_RESULT_COUNT:
        return FilterResult(
            original_conditions=original,
            applied_conditions=original,
            mongo_filter=mongo_filter,
        )

    # 2단계: 수치 조건 완화
    relaxed = [_relax(c) for c in original]
    mongo_filter_relaxed = _conditions_to_mongo(relaxed)
    if await _count_breeds(collection, mongo_filter_relaxed) >= _MIN_RESULT_COUNT:
        return FilterResult(
            original_conditions=original,
            applied_conditions=relaxed,
            mongo_filter=mongo_filter_relaxed,
            fallback_applied=True,
            fallback_reason=(
                f"원하시는 조건({', '.join(original)})을 모두 만족하는 품종이 부족해 "
                f"기준을 완화({', '.join(relaxed)})하여 검색했습니다."
            ),
        )

    # 3단계: 바이너리 조건만 유지
    binary_only = [c for c in original if _is_binary(c)]
    if binary_only:
        mongo_filter_binary = _conditions_to_mongo(binary_only)
        if await _count_breeds(collection, mongo_filter_binary) >= _MIN_RESULT_COUNT:
            removed = [c for c in original if not _is_binary(c)]
            return FilterResult(
                original_conditions=original,
                applied_conditions=binary_only,
                mongo_filter=mongo_filter_binary,
                fallback_applied=True,
                fallback_reason=(
                    f"수치 조건({', '.join(removed)})을 만족하는 품종이 부족해 "
                    f"필수 조건({', '.join(binary_only)})만 적용했습니다."
                ),
            )

    # 4단계: 조건 없음
    return FilterResult(
        original_conditions=original,
        applied_conditions=[],
        mongo_filter={},
        fallback_applied=True,
        fallback_reason="조건을 만족하는 품종이 충분하지 않아 전체 품종에서 검색합니다.",
    )
