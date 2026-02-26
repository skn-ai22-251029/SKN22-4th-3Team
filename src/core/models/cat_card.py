from pydantic import BaseModel, Field
from typing import List, Optional

class CatCardStats(BaseModel):
    """품종 통계의 전체 스펙트럼 (1-5 척도)."""
    adaptability: Optional[int] = Field(default=0)
    affection_level: Optional[int] = Field(default=0)
    child_friendly: Optional[int] = Field(default=0)
    dog_friendly: Optional[int] = Field(default=0)
    energy_level: Optional[int] = Field(default=0)
    grooming: Optional[int] = Field(default=0)
    health_issues: Optional[int] = Field(default=0)
    intelligence: Optional[int] = Field(default=0)
    shedding_level: Optional[int] = Field(default=0)
    social_needs: Optional[int] = Field(default=0)
    stranger_friendly: Optional[int] = Field(default=0)
    vocalisation: Optional[int] = Field(default=0)
    
    # 추가 정보
    weight_metric: str = Field(default="미상")
    life_span: str = Field(default="미상")
    indoor: Optional[int] = Field(default=0)
    lap: Optional[int] = Field(default=0)
    hypoallergenic: Optional[int] = Field(default=0)

class CatCardRecommendation(BaseModel):
    """UI에서 '포켓몬 카드 스타일'의 고양이 품종 카드를 렌더링하기 위한 DTO입니다."""
    name_ko: str = Field(..., description="한글 품종명")
    name_en: str = Field(..., description="영문 품종명")
    image_url: str = Field(..., description="이미지 URL (CDN 또는 로컬 경로)")
    summary: str = Field(..., description="한 줄 캐릭터 요약 (한글)")
    tags: List[str] = Field(..., description="3-4개의 해시태그 (예: ['#활동적', '#영리함'])")
    stats: CatCardStats = Field(..., description="품종에 대한 전체 통계 데이터")
