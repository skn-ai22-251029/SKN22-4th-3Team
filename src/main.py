"""
ZIPSA FastAPI 서버 엔트리포인트

실행:
  uvicorn src.main:app --reload --port 8000

엔드포인트:
  GET  /health                                    — 헬스 체크
  GET  /docs                                      — Swagger UI
  POST /api/v1/auth/sync                          — NextAuth 동기화 & JWT 발급
  GET  /api/v1/auth/me                            — 현재 유저 정보
  GET  /api/v1/users/me/profile                   — 프로필 조회
  POST /api/v1/users/me/profile                   — 프로필 생성
  PUT  /api/v1/users/me/profile                   — 프로필 수정
  GET  /api/v1/users/me/sessions                  — 세션 목록
  POST /api/v1/users/me/sessions                  — 세션 생성
  GET  /api/v1/users/me/sessions/{id}             — 세션 상세
  DELETE /api/v1/users/me/sessions/{id}           — 세션 삭제
  GET  /api/v1/users/me/sessions/{id}/messages    — 메시지 목록
  POST /api/v1/chat/invoke                        — 동기 채팅
  POST /api/v1/chat/stream                        — SSE 스트리밍
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv(Path(__file__).parents[1] / ".env")

from src.api.routers import auth, chat, meme, sessions, users

app = FastAPI(
    title="ZIPSA API",
    version="1.0.0",
    description="AI 기반 고양이 품종 매칭 및 케어 상담 서비스",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(meme.router)

# OCI_NAMESPACE 미설정 시 로컬 mock 모드
if not os.getenv("OCI_NAMESPACE"):
    from src.api.routers import dev
    app.include_router(dev.router)

    static_dir = Path(__file__).parents[1] / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
