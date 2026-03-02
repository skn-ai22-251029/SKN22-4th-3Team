"""
개발 전용 라우터 — OCI Object Storage mock 엔드포인트.

OCI_NAMESPACE 미설정 시 src/main.py에서 자동으로 포함됩니다.
프로덕션(OCI_NAMESPACE 설정됨)에서는 포함되지 않습니다.
"""
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/dev", tags=["Dev (local only)"])

STATIC_AVATARS_DIR = Path(__file__).parents[3] / "static" / "avatars"


@router.put("/avatars/{user_id}")
async def dev_avatar_upload(user_id: str, request: Request) -> JSONResponse:
    """로컬 개발용 아바타 업로드 엔드포인트 (OCI PAR mock).

    프론트엔드가 PUT {upload_url}로 파일을 전송하면
    static/avatars/{user_id} 에 저장합니다.
    """
    STATIC_AVATARS_DIR.mkdir(parents=True, exist_ok=True)
    body = await request.body()
    (STATIC_AVATARS_DIR / user_id).write_bytes(body)
    return JSONResponse({"ok": True})
