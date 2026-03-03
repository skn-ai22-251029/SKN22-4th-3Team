"""
/api/v1/chat — 커스텀 채팅 엔드포인트

POST /api/v1/chat/invoke  — 동기 응답
POST /api/v1/chat/stream  — SSE 스트리밍
"""
import json
import logging
import os
from datetime import datetime, timezone

import certifi
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from motor.motor_asyncio import AsyncIOMotorClient

import src.agents.graph as graph_module
from src.api.dependencies import get_current_user
from src.core.config import AuthConfig
from src.core.models.auth import AuthUser
from src.core.models.chat import (
    ChatInvokeRequest,
    ChatInvokeResponse,
    RagDoc,
    Recommendation,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


def _get_sessions_col():
    client = AsyncIOMotorClient(os.getenv("MONGO_V3_URI"), tlsCAFile=certifi.where())
    return client[AuthConfig.USER_DB_NAME]["chat_sessions"]


async def _get_session_or_404(session_id: str, user_id: str) -> dict:
    col = _get_sessions_col()
    doc = await col.find_one({"_id": ObjectId(session_id), "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="세션을 찾을 수 없습니다.")
    return doc


async def _update_session_meta(
    session_id: str, last_message: str, title: str | None = None, increment: int = 2
) -> None:
    """세션의 last_message, message_count, updated_at 갱신."""
    col = _get_sessions_col()
    set_fields: dict = {"last_message": last_message, "updated_at": datetime.now(timezone.utc)}
    if title is not None:
        set_fields["title"] = title
    await col.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$set": set_fields,
            "$inc": {"message_count": increment},
        },
    )


def _auto_title(message: str) -> str:
    """첫 메시지에서 세션 타이틀 자동 생성 (최대 30자)."""
    return message[:30] + ("..." if len(message) > 30 else "")


@router.post("/invoke", response_model=ChatInvokeResponse)
async def invoke_chat(
    body: ChatInvokeRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> ChatInvokeResponse:
    """동기 채팅 응답."""
    session = await _get_session_or_404(body.session_id, current_user.user_id)
    thread_id = session["thread_id"]

    result = await graph_module.app.ainvoke(
        {
            "messages": [HumanMessage(content=body.message)],
            "user_profile": {},
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    # 마지막 AIMessage 추출
    ai_messages = [m for m in result.get("messages", []) if isinstance(m, AIMessage)]
    if not ai_messages:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="응답 생성 실패")

    last_ai = ai_messages[-1]
    content = last_ai.content if isinstance(last_ai.content, str) else str(last_ai.content)

    rag_docs = [RagDoc(**d) if isinstance(d, dict) else d for d in result.get("rag_docs", [])]
    recommendations = [
        Recommendation(**r) if isinstance(r, dict) else r
        for r in result.get("recommendations", [])
    ]

    title = _auto_title(body.message) if not session.get("title") else None
    await _update_session_meta(body.session_id, body.message, title=title)

    message_id = f"{thread_id}-{len(result.get('messages', []))}"
    return ChatInvokeResponse(
        message_id=message_id,
        content=content,
        recommendations=recommendations,
        rag_docs=rag_docs,
    )


@router.post("/stream")
async def stream_chat(
    body: ChatInvokeRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> StreamingResponse:
    """SSE 스트리밍 채팅 응답."""
    session = await _get_session_or_404(body.session_id, current_user.user_id)
    thread_id = session["thread_id"]

    async def event_generator():
        full_content = ""
        rag_docs = []
        recommendations = []
        rescue_cats = []

        try:
            async for event in graph_module.app.astream_events(
                {
                    "messages": [HumanMessage(content=body.message)],
                    "user_profile": body.user_profile or {},
                },
                config={"configurable": {"thread_id": thread_id}},
                version="v2",
            ):
                kind = event.get("event")
                tags = event.get("tags", [])

                # router_classification 태그 필터링 (내부 LLM 호출 제외)
                if "router_classification" in tags:
                    continue

                if kind == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        full_content += chunk.content
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

                elif kind == "on_chain_end":
                    output = event.get("data", {}).get("output", {})
                    if isinstance(output, dict):
                        if output.get("rag_docs"):
                            rag_docs = output["rag_docs"]
                            yield f"data: {json.dumps({'type': 'rag_docs', 'data': rag_docs})}\n\n"
                        if output.get("recommendations"):
                            recommendations = output["recommendations"]
                            yield f"data: {json.dumps({'type': 'recommendations', 'data': recommendations})}\n\n"
                        if output.get("rescue_cats"):
                            rescue_cats = output["rescue_cats"]
                            yield f"data: {json.dumps({'type': 'rescue_cats', 'data': rescue_cats})}\n\n"

        except Exception:
            logger.exception("stream_chat 오류")
            yield f"data: {json.dumps({'type': 'error', 'content': '응답 생성 중 오류가 발생했습니다.'})}\n\n"
        finally:
            if full_content:
                title = _auto_title(body.message) if not session.get("title") else None
                await _update_session_meta(body.session_id, body.message, title=title)
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
