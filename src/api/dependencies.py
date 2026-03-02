"""
공통 FastAPI 의존성.
"""
import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import AuthConfig
from src.core.models.auth import AuthUser

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> AuthUser:
    """Authorization: Bearer <token> 헤더에서 JWT를 검증하고 AuthUser를 반환합니다."""
    secret = os.getenv("ZIPSA_JWT_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 설정 오류: JWT 시크릿 미설정",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=[AuthConfig.JWT_ALGORITHM],
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if not user_id or not email:
            raise ValueError("토큰 페이로드 불완전")
        return AuthUser(user_id=user_id, email=email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다.",
        )
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        )
