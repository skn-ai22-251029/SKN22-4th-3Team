from pydantic import BaseModel, Field
from typing import List, Optional

class ArticleMetadataV1(BaseModel):
    """Schema for LLM extraction in V1 (Legacy)."""
    category: str = Field(description="Single category from standardized list")
    keywords: List[str] = Field(description="Top 3 keywords")
    summary: str = Field(description="One sentence summary of the article")
    potential_questions: List[str] = Field(description="Top 2 potential questions")

class StoredDocumentV1(ArticleMetadataV1):
    """Schema for final storage in MongoDB for V1."""
    uid: str = Field(description="Unique identifier (e.g., guide_00001)")
    title: str = Field(description="Original title")
    text: str = Field(description="Original cleaned text")
    tokenized_text: str = Field(description="Tokenized text for keyword search")
    embedding: Optional[List[float]] = Field(default=None, description="1536-dim vector")
    source: str = "bemypet_catlab"

class BatchResultV1(BaseModel):
    results: List[ArticleMetadataV1]
