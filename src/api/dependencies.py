"""
공통 FastAPI 의존성.

JWT 검증 등 인증 로직은 Issue #20에서 구현 예정.
"""
from fastapi import HTTPException, status


async def get_current_user() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="인증 미구현",
    )
