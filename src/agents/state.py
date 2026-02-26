"""
LangGraph 워크플로우 에이전트 상태 정의
"""
from typing import Annotated, Sequence, Dict, Any, Optional, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(Dict[str, Any]):
    """
    고양이 집사 서비스 상태.

    - messages: 사용자 대화 전용 (HumanMessage + 최종 AIMessage)
    - specialist_result: 전문가 노드의 구조화된 JSON (내부 통신용)
    """
    # 사용자 대화 (HumanMessage + 집사의 최종 AIMessage만 포함)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_profile: Dict[str, Any]

    # 라우팅
    router_decision: Optional[str]

    # 내부: 전문가 → 집사 구조화된 결과
    specialist_result: Optional[Dict[str, Any]]

    # UI용 결과 (품종 카드, RAG 출처)
    recommendations: Optional[List[Dict[str, Any]]]
    rag_docs: Optional[List[Dict[str, Any]]]
