"""
ZIPSA FastAPI 서버 엔트리포인트

실행:
  uvicorn src.main:app --reload --port 8000

엔드포인트:
  GET  /health                      — 헬스 체크
  GET  /docs                        — Swagger UI
  POST /api/v1/chat/invoke          — 동기 응답
  POST /api/v1/chat/stream          — SSE 스트리밍
  POST /api/v1/chat/stream_events   — astream_events v2
"""
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).parents[1] / ".env")

from src.api.routers import auth, chat, meme, users

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

app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(meme.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
