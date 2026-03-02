"""
/api/v1/users — 유저 프로필 라우터
"""
import logging
import os
from datetime import datetime, timezone

import certifi
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from src.api.dependencies import get_current_user
from src.core.config import AuthConfig
from src.core.models.auth import AuthUser
from src.core.models.profile import (
    UserProfileCreateRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def _get_profiles_collection():
    uri = os.getenv("MONGO_V3_URI")
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    return client[AuthConfig.USER_DB_NAME]["user_profiles"]


def _get_users_collection():
    uri = os.getenv("MONGO_V3_URI")
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    return client[AuthConfig.USER_DB_NAME]["users"]


def _doc_to_response(doc: dict, email: str) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=str(doc["user_id"]),
        email=email,
        nickname=doc.get("nickname"),
        age=doc.get("age"),
        gender=doc.get("gender"),
        contact=doc.get("contact"),
        address=doc.get("address"),
        avatar_url=doc.get("avatar_url"),
        preferences=doc.get("preferences", {}),
        onboarding_completed=doc.get("onboarding_completed", False),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: AuthUser = Depends(get_current_user),
) -> UserProfileResponse:
    """내 프로필 조회. 없으면 404."""
    profiles = _get_profiles_collection()
    doc = await profiles.find_one({"user_id": current_user.user_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="프로필 없음 (온보딩 미완료)")
    return _doc_to_response(doc, current_user.email)


@router.post("/me/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    body: UserProfileCreateRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> UserProfileResponse:
    """프로필 생성 (온보딩 완료). 이미 존재하면 409."""
    profiles = _get_profiles_collection()
    existing = await profiles.find_one({"user_id": current_user.user_id})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 프로필이 존재합니다.")

    now = datetime.now(timezone.utc)
    doc = {
        "user_id": current_user.user_id,
        **body.model_dump(),
        "onboarding_completed": True,
        "created_at": now,
        "updated_at": now,
    }
    await profiles.insert_one(doc)
    return _doc_to_response(doc, current_user.email)


@router.post("/me/profile/avatar/presign")
async def get_avatar_presign_url(
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """OCI Object Storage Pre-Authenticated Request URL 발급.

    클라이언트는 반환된 upload_url로 PUT 요청을 보내 파일을 업로드합니다.
    업로드 완료 후 avatar_url을 PUT /me/profile에 포함하여 프로필을 갱신합니다.
    """
    from src.api.oci_storage import generate_avatar_par
    return await generate_avatar_par(str(current_user.user_id))


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_profile(
    body: UserProfileUpdateRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> UserProfileResponse:
    """프로필 수정. 없으면 404."""
    profiles = _get_profiles_collection()
    now = datetime.now(timezone.utc)

    update_fields = {k: v for k, v in body.model_dump().items() if v is not None}
    update_fields["updated_at"] = now

    doc = await profiles.find_one_and_update(
        {"user_id": current_user.user_id},
        {"$set": update_fields},
        return_document=True,
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="프로필 없음 (온보딩 미완료)")
    return _doc_to_response(doc, current_user.email)
