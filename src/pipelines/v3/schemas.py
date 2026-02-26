from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractionMetadataV3(BaseModel):
    """V3(Clean)의 LLM 추출용 스키마입니다."""
    summary: str = Field(description="전문적인 한국어로 된 한 문장 요약")
    keywords: List[str] = Field(description="3~5개의 핵심 키워드")
    intent_tags: List[str] = Field(description="의도 태그 (예: '응급', '일상 케어')")

class ExtractionArticleV3(BaseModel):
    """V3에서 각 기사에 대해 LLM이 반환하는 구조화된 결과입니다."""
    title_refined: str = Field(description="검색 최적화된 정제된 제목")
    metadata: ExtractionMetadataV3
    categories: List[str] = Field(description="표준화된 영문 카테고리")
    specialists: List[str] = Field(description="표준화된 영문 페르소나")

class StoredDocumentV3(ExtractionArticleV3):
    """V3(Clean)의 MongoDB 최종 저장용 스키마입니다."""
    uid: str = Field(description="최종 고유 ID (예: v3_00001)")
    text: str = Field(description="기사의 전체 원문 텍스트")
    tokenized_text: str = Field(description="사용자 사전을 적용하여 형태소 분석된 전체 텍스트")
    embedding: Optional[List[float]] = Field(default=None, description="OpenAI 구조화 임베딩")
    source: str = "bemypet_catlab"
    original_url: Optional[str] = None

class BatchResultV3(BaseModel):
    results: List[ExtractionArticleV3]

class BreedStats(BaseModel):
    weight_metric: str = "미상"
    life_span: str = "미상"
    indoor: Optional[int] = 0
    lap: Optional[int] = 0
    hypoallergenic: Optional[int] = 0
    adaptability: Optional[int] = 0
    affection_level: Optional[int] = 0
    child_friendly: Optional[int] = 0
    dog_friendly: Optional[int] = 0
    energy_level: Optional[int] = 0
    grooming: Optional[int] = 0
    health_issues: Optional[int] = 0
    intelligence: Optional[int] = 0
    shedding_level: Optional[int] = 0
    social_needs: Optional[int] = 0
    stranger_friendly: Optional[int] = 0
    vocalisation: Optional[int] = 0

class StoredBreedV3(BaseModel):
    """V3 품종 컬렉션용 스키마입니다."""
    uid: str = Field(description="고유 ID (예: breed_abys)")
    title_refined: str = Field(description="리트리버 호환성을 위한 통합 제목 필드")
    name_ko: str = Field(description="한글 품종명")
    name_en: str
    summary: str
    personality_traits: List[str]
    physical_traits: List[str]
    stats: BreedStats
    text: str = Field(description="RAG 컨텍스트를 위한 전체 설명")
    tokenized_text: str = Field(description="Kiwi로 형태소 분석된 텍스트")
    embedding: Optional[List[float]] = None
    image_url: Optional[str] = Field(default=None, description="TheCatAPI CDN URL")
    source: str = "thecatapi_integrated"
    categories: List[str] = ["Breeds"]
    specialists: List[str] = ["Matchmaker"]
    
    # [메타데이터 필터] Atlas 벡터 검색용
    # 검색 및 필터링 편의를 위해 stats에서 복사됨
    filter_shedding: Optional[int] = Field(default=0, description="필터링을 위한 stats.shedding_level 복사본")
    filter_energy: Optional[int] = Field(default=0, description="필터링을 위한 stats.energy_level 복사본")
    filter_intelligence: Optional[int] = Field(default=0, description="필터링을 위한 stats.intelligence 복사본")
    filter_affection: Optional[int] = Field(default=0, description="필터링을 위한 stats.affection_level 복사본")
    filter_child_friendly: Optional[int] = Field(default=0, description="필터링을 위한 stats.child_friendly 복사본")
    filter_indoor: Optional[int] = Field(default=0, description="필터링을 위한 stats.indoor 복사본")
    filter_lap: Optional[int] = Field(default=0, description="필터링을 위한 stats.lap 복사본")
    filter_hypoallergenic: Optional[int] = Field(default=0, description="필터링을 위한 stats.hypoallergenic 복사본")
    filter_adaptability: Optional[int] = Field(default=0, description="필터링을 위한 stats.adaptability 복사본")
    filter_dog_friendly: Optional[int] = Field(default=0, description="필터링을 위한 stats.dog_friendly 복사본")
    filter_grooming: Optional[int] = Field(default=0, description="필터링을 위한 stats.grooming 복사본")
    filter_health_issues: Optional[int] = Field(default=0, description="필터링을 위한 stats.health_issues 복사본")
    filter_social_needs: Optional[int] = Field(default=0, description="필터링을 위한 stats.social_needs 복사본")
    filter_stranger_friendly: Optional[int] = Field(default=0, description="필터링을 위한 stats.stranger_friendly 복사본")
    filter_vocalisation: Optional[int] = Field(default=0, description="필터링을 위한 stats.vocalisation 복사본")
