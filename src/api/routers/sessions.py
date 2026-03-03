"""
/api/v1/users/me/sessions — 채팅 세션 CRUD
"""
import logging
import os
from datetime import datetime, timezone

import certifi
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from motor.motor_asyncio import AsyncIOMotorClient

import src.agents.graph as graph_module
from src.api.dependencies import get_current_user
from src.core.config import AuthConfig
from src.core.models.auth import AuthUser
from src.core.models.chat import (
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionResponse,
    RagDoc,
    Recommendation,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users/me/sessions", tags=["Chat Sessions"])


def _get_sessions_col():
    client = AsyncIOMotorClient(os.getenv("MONGO_V3_URI"), tlsCAFile=certifi.where())
    return client[AuthConfig.USER_DB_NAME]["chat_sessions"]




def _doc_to_response(doc: dict) -> ChatSessionResponse:
    return ChatSessionResponse(
        session_id=str(doc["_id"]),
        user_id=doc["user_id"],
        thread_id=doc["thread_id"],
        title=doc.get("title"),
        last_message=doc.get("last_message"),
        message_count=doc.get("message_count", 0),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("", response_model=list[ChatSessionResponse])
async def list_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthUser = Depends(get_current_user),
) -> list[ChatSessionResponse]:
    col = _get_sessions_col()
    cursor = col.find({"user_id": current_user.user_id}).sort("updated_at", -1).skip(offset).limit(limit)
    return [_doc_to_response(doc) async for doc in cursor]


@router.post("", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: ChatSessionCreateRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> ChatSessionResponse:
    col = _get_sessions_col()
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": current_user.user_id,
        "title": body.title,
        "last_message": None,
        "message_count": 0,
        "created_at": now,
        "updated_at": now,
    }
    result = await col.insert_one(doc)
    doc["_id"] = result.inserted_id
    # thread_id = session_id (LangGraph MongoDBSaver 연동)
    session_id = str(result.inserted_id)
    await col.update_one({"_id": result.inserted_id}, {"$set": {"thread_id": session_id}})
    doc["thread_id"] = session_id
    return _doc_to_response(doc)


@router.get("/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> ChatSessionResponse:
    col = _get_sessions_col()
    doc = await col.find_one({"_id": ObjectId(session_id), "user_id": current_user.user_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="세션을 찾을 수 없습니다.")
    return _doc_to_response(doc)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> None:
    col = _get_sessions_col()
    result = await col.delete_one({"_id": ObjectId(session_id), "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="세션을 찾을 수 없습니다.")
    # LangGraph 체크포인트 삭제
    await graph_module.app.checkpointer.adelete_thread(session_id)


@router.get("/{session_id}/messages", response_model=list[ChatMessageResponse])
async def list_messages(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    current_user: AuthUser = Depends(get_current_user),
) -> list[ChatMessageResponse]:
    """LangGraph MongoDBSaver 체크포인트에서 메시지 복원."""
    col = _get_sessions_col()
    session = await col.find_one({"_id": ObjectId(session_id), "user_id": current_user.user_id})
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="세션을 찾을 수 없습니다.")

    state = await graph_module.app.aget_state({"configurable": {"thread_id": session_id}})
    if not state or not state.values:
        return []

    messages = state.values.get("messages", [])
    result = []
    for i, msg in enumerate(messages[-limit:]):
        # ToolMessage와 내용 없는 AIMessage(tool call 전용) 제외
        if isinstance(msg, ToolMessage):
            continue
        if isinstance(msg, AIMessage) and not msg.content:
            continue

        role = "human" if isinstance(msg, HumanMessage) else "ai"
        rag_docs = []
        recommendations = []
        rescue_cats = []
        if isinstance(msg, AIMessage):
            for doc in state.values.get("rag_docs", []):
                rag_docs.append(RagDoc(**doc) if isinstance(doc, dict) else doc)
            for rec in state.values.get("recommendations", []):
                recommendations.append(Recommendation(**rec) if isinstance(rec, dict) else rec)
            for cat in state.values.get("rescue_cats", []):
                rescue_cats.append(cat)
        result.append(ChatMessageResponse(
            message_id=f"{session_id}-{i}",
            session_id=session_id,
            role=role,
            content=msg.content if isinstance(msg.content, str) else str(msg.content),
            recommendations=recommendations,
            rag_docs=rag_docs,
            rescue_cats=rescue_cats,
            created_at=session["created_at"],
        ))
    return result
