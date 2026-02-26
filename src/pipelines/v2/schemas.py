from pydantic import BaseModel, Field
from typing import List, Optional

class ArticleMetadataV2(BaseModel):
    """Schema for LLM extraction in V2 (Pro)."""
    categories: List[str] = Field(description="Multiple categories")
    specialists: List[str] = Field(description="Mapped specialist personas")
    keywords: List[str] = Field(description="3-5 핵심 키워드")
    summary: str = Field(description="1-2문장 한국어 요약")
    potential_questions: List[str] = Field(description="2-3 예상 질문")
    target_audience: str = Field(description="대상 독자 (예: 초보 집사)")
    entities: List[str] = Field(description="언급된 품종, 질병 등 주요 개체")

class StoredDocumentV2(ArticleMetadataV2):
    """Schema for final storage in MongoDB for V2."""
    uid: str = Field(description="Unique identifier")
    title: str = Field(description="Original title")
    text: str = Field(description="Original cleaned text")
    tokenized_text: str = Field(description="Tokenized text for keyword search")
    embedding: Optional[List[float]] = Field(default=None, description="1536-dim vector")
    source: str = "bemypet_catlab"

class BatchResultV2(BaseModel):
    results: List[ArticleMetadataV2]
