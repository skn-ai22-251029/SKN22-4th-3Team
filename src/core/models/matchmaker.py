from typing import List, Literal
from pydantic import BaseModel, Field

class BreedSelection(BaseModel):
    """에이전틱 선별용 구조화된 출력."""
    selected_indices: List[int] = Field(..., max_items=3, description="후보 목록에서 선택한 품종 인덱스")
    reasoning: str = Field(..., description="해당 3종을 선택한 이유")

class SearchIntent(BaseModel):
    """사용자 질문의 검색 의도 분류"""
    category: Literal["LOOKUP", "RECOMMEND"] = Field(
        ..., 
        description=(
            "LOOKUP: 특정 품종에 대한 단순 정보/특징 조회 (예: '메인쿤 성격 어때?', '페르시안 특징'). "
            "RECOMMEND: 사용자 환경에 맞는 추천 요청 (예: '나한테 맞는 고양이', '털 안빠지는 묘종 추천')"
        )
    )
    keywords: str = Field(..., description="검색 엔진에 전달할 핵심 키워드 (예: '메인쿤', '대형묘', '저자극성 고양이')")
