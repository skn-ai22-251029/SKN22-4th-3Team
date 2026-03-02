"""
채팅 세션 및 메시지 Pydantic 모델.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── 세션 ──────────────────────────────────────────────────────────────────────

class ChatSessionCreateRequest(BaseModel):
    title: Optional[str] = Field(default=None, description="null이면 첫 메시지 기반 자동 생성")


class ChatSessionResponse(BaseModel):
    session_id: str
    user_id: str
    thread_id: str
    title: Optional[str] = None
    last_message: Optional[str] = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


# ── 메시지 ─────────────────────────────────────────────────────────────────────

class RagDoc(BaseModel):
    title: str = ""
    subtitle: str = ""
    source: str = ""
    url: str = ""


class Recommendation(BaseModel):
    name_ko: str = ""
    name_en: Optional[str] = None
    image_url: Optional[str] = None
    summary: str = ""
    tags: List[str] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)


class RescueCat(BaseModel):
    animal_id: str = ""
    breed: str = ""
    age: str = ""
    sex: str = ""
    neutered: str = ""
    feature: str = ""
    image_url: str = ""
    shelter_name: str = ""
    shelter_address: str = ""
    shelter_phone: str = ""
    notice_end_date: str = ""
    sido: str = ""
    sigungu: str = ""


class ChatMessageResponse(BaseModel):
    message_id: str
    session_id: str
    role: str  # "human" | "ai"
    content: str
    recommendations: List[Recommendation] = Field(default_factory=list)
    rag_docs: List[RagDoc] = Field(default_factory=list)
    rescue_cats: List[RescueCat] = Field(default_factory=list)
    created_at: datetime


# ── Chat 호출 ─────────────────────────────────────────────────────────────────

class ChatInvokeRequest(BaseModel):
    session_id: str
    message: str
    user_profile: Optional[Dict[str, Any]] = Field(default=None, description="프론트에서 전달하는 온보딩 프로파일")


class ChatInvokeResponse(BaseModel):
    message_id: str
    content: str
    recommendations: List[Recommendation] = Field(default_factory=list)
    rag_docs: List[RagDoc] = Field(default_factory=list)
    rescue_cats: List[RescueCat] = Field(default_factory=list)
