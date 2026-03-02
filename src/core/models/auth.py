"""
인증 관련 Pydantic 모델.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AuthUser(BaseModel):
    """JWT에서 추출한 인증된 유저 정보."""
    user_id: str = Field(description="MongoDB users._id (문자열)")
    email: str = Field(description="OAuth 이메일")


class SyncRequest(BaseModel):
    """POST /auth/sync — NextAuth 세션 정보."""
    email: str = Field(description="OAuth 이메일")
    name: Optional[str] = Field(default=None, description="표시 이름")
    image: Optional[str] = Field(default=None, description="프로필 이미지 URL")
    provider: str = Field(description="OAuth 프로바이더 (google | kakao | naver)")


class SyncResponse(BaseModel):
    """POST /auth/sync 응답 — ZIPSA 액세스 토큰."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class MeResponse(BaseModel):
    """GET /auth/me 응답."""
    user_id: str
    email: str
    name: Optional[str] = None
    image: Optional[str] = None
    provider: Optional[str] = None
