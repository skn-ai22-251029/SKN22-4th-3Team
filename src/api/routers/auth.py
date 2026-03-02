"""
/api/v1/auth — 인증 라우터

POST /api/v1/auth/sync  — NextAuth 세션 → MongoDB upsert → ZIPSA JWT 발급
GET  /api/v1/auth/me    — 현재 로그인 유저 정보 조회
"""
import logging
import os
from datetime import datetime, timedelta, timezone

import certifi
import jwt
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import AuthConfig
from src.core.models.auth import AuthUser, MeResponse, SyncRequest, SyncResponse
from src.api.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


def _get_users_collection():
    uri = os.getenv("MONGO_V3_URI")
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    return client[AuthConfig.USER_DB_NAME]["users"]


def _issue_token(user_id: str, email: str) -> str:
    secret = os.getenv("ZIPSA_JWT_SECRET")
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=AuthConfig.JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, secret, algorithm=AuthConfig.JWT_ALGORITHM)


@router.post("/sync", response_model=SyncResponse, status_code=status.HTTP_200_OK)
async def sync_user(body: SyncRequest) -> SyncResponse:
    """
    NextAuth 로그인 후 호출. users 컬렉션에 upsert하고 ZIPSA JWT를 반환합니다.
    """
    collection = _get_users_collection()
    now = datetime.now(timezone.utc)

    result = await collection.find_one_and_update(
        {"email": body.email},
        {
            "$set": {
                "email": body.email,
                "name": body.name,
                "image": body.image,
                "provider": body.provider,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
        return_document=True,
    )

    user_id = str(result["_id"])
    access_token = _issue_token(user_id, body.email)

    return SyncResponse(
        access_token=access_token,
        user_id=user_id,
        email=body.email,
    )


@router.get("/me", response_model=MeResponse)
async def get_me(current_user: AuthUser = Depends(get_current_user)) -> MeResponse:
    """JWT에서 user_id를 추출해 MongoDB에서 유저 정보를 조회합니다."""
    collection = _get_users_collection()
    try:
        doc = await collection.find_one({"_id": ObjectId(current_user.user_id)})
    except Exception:
        doc = None

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유저를 찾을 수 없습니다.")

    return MeResponse(
        user_id=str(doc["_id"]),
        email=doc.get("email", current_user.email),
        name=doc.get("name"),
        image=doc.get("image"),
        provider=doc.get("provider"),
    )
