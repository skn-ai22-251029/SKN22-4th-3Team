"""
내 고양이 Pydantic 모델.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class VaccinationInfo(BaseModel):
    label: str = ""
    date: str = ""


class UserCatHealth(BaseModel):
    vaccinations: List[VaccinationInfo] = Field(default_factory=list)


class UserCatCreateRequest(BaseModel):
    name: str
    age_months: int = 0
    gender: str = "미상"  # "M" | "F" | "미상"
    breed_name_ko: str = ""
    breed_name_en: str = ""
    profile_image_url: Optional[str] = None
    meme_text: Optional[str] = None
    health: Optional[UserCatHealth] = None


class UserCatUpdateRequest(BaseModel):
    name: Optional[str] = None
    age_months: Optional[int] = None
    gender: Optional[str] = None
    breed_name_ko: Optional[str] = None
    breed_name_en: Optional[str] = None
    profile_image_url: Optional[str] = None
    meme_text: Optional[str] = None
    health: Optional[UserCatHealth] = None


class UserCatResponse(BaseModel):
    cat_id: str
    user_id: str
    name: str
    age_months: int = 0
    gender: str = "미상"
    breed_name_ko: str = ""
    breed_name_en: str = ""
    profile_image_url: Optional[str] = None
    meme_text: Optional[str] = None
    health: UserCatHealth = Field(default_factory=UserCatHealth)
    created_at: datetime
    updated_at: datetime
