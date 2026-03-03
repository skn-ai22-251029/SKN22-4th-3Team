"""
/api/v1/users/me/cats — 유저 고양이 CRUD
"""
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import certifi
from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorClient

from src.api.dependencies import get_current_user
from src.core.config import AuthConfig
from src.core.models.auth import AuthUser
from src.core.models.user_cat import (
    UserCatCreateRequest,
    UserCatHealth,
    UserCatResponse,
    UserCatUpdateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users/me/cats", tags=["Cats"])


def _get_cats_col():
    uri = os.getenv("MONGO_V3_URI")
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    return client[AuthConfig.USER_DB_NAME]["user_cats"]


def _doc_to_response(doc: dict) -> UserCatResponse:
    health_data = doc.get("health") or {}
    return UserCatResponse(
        cat_id=str(doc["_id"]),
        user_id=str(doc["user_id"]),
        name=doc["name"],
        age_months=doc.get("age_months", 0),
        gender=doc.get("gender", "미상"),
        breed_name_ko=doc.get("breed_name_ko", ""),
        breed_name_en=doc.get("breed_name_en", ""),
        profile_image_url=doc.get("profile_image_url"),
        meme_text=doc.get("meme_text"),
        health=UserCatHealth(**health_data) if health_data else UserCatHealth(),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("", response_model=list[UserCatResponse])
async def list_cats(
    current_user: AuthUser = Depends(get_current_user),
) -> list[UserCatResponse]:
    """내 고양이 목록 조회."""
    col = _get_cats_col()
    cursor = col.find({"user_id": current_user.user_id})
    docs = await cursor.to_list(length=100)
    return [_doc_to_response(d) for d in docs]


@router.post("", response_model=UserCatResponse, status_code=status.HTTP_201_CREATED)
async def create_cat(
    body: UserCatCreateRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> UserCatResponse:
    """고양이 등록."""
    col = _get_cats_col()
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": current_user.user_id,
        **body.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    result = await col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_response(doc)


@router.get("/{cat_id}", response_model=UserCatResponse)
async def get_cat(
    cat_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> UserCatResponse:
    """고양이 상세 조회."""
    col = _get_cats_col()
    doc = await col.find_one({"_id": ObjectId(cat_id), "user_id": current_user.user_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="고양이를 찾을 수 없습니다.")
    return _doc_to_response(doc)


@router.put("/{cat_id}", response_model=UserCatResponse)
async def update_cat(
    cat_id: str,
    body: UserCatUpdateRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> UserCatResponse:
    """고양이 정보 수정."""
    col = _get_cats_col()
    now = datetime.now(timezone.utc)
    update_fields = {k: v for k, v in body.model_dump().items() if v is not None}
    update_fields["updated_at"] = now
    doc = await col.find_one_and_update(
        {"_id": ObjectId(cat_id), "user_id": current_user.user_id},
        {"$set": update_fields},
        return_document=True,
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="고양이를 찾을 수 없습니다.")
    return _doc_to_response(doc)


@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cat(
    cat_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> None:
    """고양이 삭제."""
    col = _get_cats_col()
    result = await col.delete_one({"_id": ObjectId(cat_id), "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="고양이를 찾을 수 없습니다.")


_CATS_STATIC_DIR = Path(__file__).parents[3] / "static" / "cats"


@router.post("/upload-image")
async def upload_cat_image(
    image: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """고양이 프로필 이미지 업로드 → /static/cats/{uuid}.jpg URL 반환."""
    _CATS_STATIC_DIR.mkdir(parents=True, exist_ok=True)
    image_bytes = await image.read()
    ext = Path(image.filename or "image.jpg").suffix or ".jpg"
    file_name = f"{uuid.uuid4()}{ext}"
    (_CATS_STATIC_DIR / file_name).write_bytes(image_bytes)
    return {"image_url": f"/static/cats/{file_name}"}
