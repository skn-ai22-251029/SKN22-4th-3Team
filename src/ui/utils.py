"""
에이전트 응답 실시간 스트리밍 유틸리티.

비동기 제너레이터를 통해 에이전트 추론 과정 및 채팅 응답을 스트리밍.
"""
import asyncio
import logging
from src.agents.graph import app
from langchain_core.messages import HumanMessage, AIMessageChunk
from src.core.models.debug import AgentTrace, DebugLevel
from typing import AsyncGenerator, Tuple, Dict, Any, List

logger = logging.getLogger(__name__)


async def get_zipsa_response_streaming(
    user_input: str,
    user_profile: dict,
    history: list,
    thread_id: str = "default_session"
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    LangGraph astream_events를 이용한 에이전트 응답 실시간 스트리밍.

    Yields:
        dict: 이벤트 딕셔너리
            - type: "status" | "response" | "complete" | "error"
            - content: str
            - metadata: dict (선택)
    """
    new_message = HumanMessage(content=user_input)
    agent_trace = AgentTrace(session_id=thread_id)

    inputs = {
        "messages": [new_message],
        "user_profile": user_profile.model_dump() if hasattr(user_profile, "model_dump") else (user_profile or {}),
        "agent_trace": agent_trace,
        "debug_level": DebugLevel.STANDARD
    }

    config = {"configurable": {"thread_id": thread_id}}

    final_content = ""
    recommendations = []
    rag_docs = []
    current_node = ""

    NODE_STATUS = {
        "head_butler": "🎩 집사가 질문을 분석하고 있습니다...",
        "matchmaker": "🧩 매치메이커가 품종을 탐색 중입니다...",
        "care": "🩺 케어팀이 상담 중입니다...",
        "liaison": "🔭 리에종이 정보를 조회 중입니다...",
        "tools": "🔍 외부 데이터를 검색 중입니다...",
    }

    try:
        # astream_events v2로 LLM 토큰 스트리밍 캡처
        async for event in app.astream_events(inputs, config, version="v2"):
            kind = event.get("event", "")

            # 현재 활성 노드 추적
            if kind == "on_chain_start":
                node_name = event.get("name", "")
                if node_name in NODE_STATUS and node_name != current_node:
                    current_node = node_name
                    yield {
                        "type": "reasoning",
                        "content": NODE_STATUS[node_name] + "\n"
                    }

            # 집사의 최종 응답에서 LLM 토큰 스트리밍 캡처
            if kind == "on_chat_model_stream":
                tags = event.get("tags", [])
                
                # 내부 라우팅/분류 JSON을 사용자 화면에서 필터링
                if "router_classification" in tags:
                    continue
                
                parent_ids = event.get("parent_ids", [])
                chunk = event.get("data", {}).get("chunk")

                if chunk and hasattr(chunk, "content") and chunk.content:
                    # 집사의 최종 사용자 응답만 스트리밍
                    # 집사는 라우팅에 structured output(content 없음)을 사용하므로
                    # content가 있는 스트림은 최종 응답임
                    token = chunk.content
                    final_content += token
                    yield {
                        "type": "response",
                        "content": token
                    }

            # 체인 종료 시 최종 상태 캡처
            if kind == "on_chain_end" and event.get("name") == "LangGraph":
                output = event.get("data", {}).get("output", {})
                if isinstance(output, dict):
                    recommendations = output.get("recommendations", [])

        # 체인 종료 후 최종 상태 값 캡처
        state = app.get_state(config)
        if state and state.values:
            recommendations = state.values.get("recommendations", []) or recommendations
            rag_docs = state.values.get("rag_docs", []) or rag_docs
            
            # 스트리밍 토큰이 캡처되지 않은 경우 (비스트리밍 모델 또는 오류),
            # 최종 상태 메시지에서 컨텐츠 가져옴
            if not final_content:
                messages = state.values.get("messages", [])
                if messages:
                    final_content = messages[-1].content
                    yield {
                        "type": "response",
                        "content": final_content
                    }

        yield {
            "type": "complete",
            "content": final_content,
            "metadata": {
                "recommendations": recommendations,
                "rag_docs": rag_docs
            }
        }

    except Exception as e:
        logger.exception("스트리밍 오류")
        yield {
            "type": "error",
            "content": f"오류 발생: {str(e)}"
        }
