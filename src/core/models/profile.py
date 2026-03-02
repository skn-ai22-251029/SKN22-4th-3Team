"""
프로필 API Pydantic 모델.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    """온보딩 선호 데이터."""
    housing: str = Field(default="apartment")
    activity: str = Field(default="low")
    experience: str = Field(default="beginner")
    work_style: Optional[str] = None
    allergy: bool = False
    has_children: bool = False
    has_dog: bool = False
    has_cat: bool = False
    traits: List[str] = Field(default_factory=list)
    companion: List[str] = Field(default_factory=list)


class UserProfileCreateRequest(BaseModel):
    """POST /users/me/profile 요청."""
    nickname: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)


class UserProfileUpdateRequest(BaseModel):
    """PUT /users/me/profile 요청 — 모든 필드 선택적."""
    nickname: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class UserProfileResponse(BaseModel):
    """프로필 응답."""
    user_id: str
    email: str
    nickname: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    onboarding_completed: bool = False
    created_at: datetime
    updated_at: datetime
