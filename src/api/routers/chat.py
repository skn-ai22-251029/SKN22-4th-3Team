"""
/api/v1/chat — LangServe 라우터

LangServe add_routes가 자동 생성하는 엔드포인트:
  POST /api/v1/chat/invoke          — 동기 응답
  POST /api/v1/chat/stream          — SSE 스트리밍
  POST /api/v1/chat/stream_events   — astream_events v2
  GET  /api/v1/chat/input_schema    — 입력 스키마
  GET  /api/v1/chat/output_schema   — 출력 스키마

Note:
  AgentState가 Dict[str, Any] 서브클래스라 Pydantic v2가 JSON 스키마를
  자동 생성할 수 없으므로, 명시적 ChatInput 모델을 input_type으로 전달한다.
  LangServe는 이를 dict로 변환하여 그래프에 전달하므로 동작에는 영향 없음.
"""
from typing import Any, Dict, List

from fastapi import APIRouter
from langserve import add_routes
from pydantic import BaseModel

from src.agents.graph import app as graph_app


class ChatInput(BaseModel):
    """LangServe /invoke, /stream 공통 입력 스키마."""

    messages: List[Dict[str, Any]]
    user_profile: Dict[str, Any] = {}


router = APIRouter()
add_routes(
    router,
    graph_app,
    path="/api/v1/chat",
    input_type=ChatInput,
    config_keys=["configurable"],  # thread_id 등 LangGraph 체크포인터 설정 전달
)
