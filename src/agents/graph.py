"""
LangGraph 워크플로우 정의 (고양이 집사 서비스)
4노드 아키텍처: head_butler → matchmaker | liaison | care
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from .state import AgentState
from .head_butler import head_butler_node
from .matchmaker import matchmaker_node
from .liaison import liaison_node
from .care_team import care_team_node
from .tools.animal_protection import search_abandoned_animals


tools = [search_abandoned_animals]
tool_node = ToolNode(tools)


def create_zipsa_graph():
    """
    에이전트 그래프 생성:
    - head_butler: 메인 라우터 겸 유일한 종료 지점. 모든 전문가의 결과는 여기로 모임.
    - matchmaker: 품종 추천 (RAG specialist=Matchmaker)
    - liaison: 입양/구조 정보 (RAG specialist=Liaison + 동물보호 API 도구)
    - tools: 국가동물보호정보시스템 조회 (liaison이 호출)
    - care: 건강 + 행동 상담 (Physician + Peacekeeper 통합)
    
    참고: 각 노드는 Command(goto=...)를 사용하여 동적 라우팅을 수행하므로, 
    아래 정의된 static edges는 주로 그래프 시각화 및 구조 명시용으로 작동합니다.
    """

    memory = MemorySaver()
    workflow = StateGraph(AgentState)

    # 1. 노드 등록 (Node Registration)
    workflow.add_node("head_butler", head_butler_node)
    workflow.add_node("matchmaker", matchmaker_node)
    workflow.add_node("liaison", liaison_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("care", care_team_node)

    # 2. 라우팅 로직 (Static Routing for Visualization)
    def route_butler(state: AgentState):
        """수석 집사의 분류 결과에 따라 전문가로 라우팅"""
        decision = state.get("router_decision", "general")
        if decision in ("matchmaker", "liaison", "care"):
            return decision
        return END

    def route_liaison(state: AgentState):
        """리에종이 도구 호출(API)을 요청했는지 확인"""
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "tools"
        return "head_butler"

    # 3. 그래프 구성 (Graph Edges)
    workflow.add_edge(START, "head_butler")

    # 수석 집사: 전문가 라우팅 또는 종료
    workflow.add_conditional_edges(
        "head_butler",
        route_butler,
        {"matchmaker": "matchmaker", "liaison": "liaison", "care": "care", END: END}
    )

    # 매치메이커 -> 수석 집사
    workflow.add_edge("matchmaker", "head_butler")

    # 리에종 -> 도구(API) 또는 수석 집사
    workflow.add_conditional_edges(
        "liaison",
        route_liaison,
        {"tools": "tools", "head_butler": "head_butler"}
    )

    # 도구(API) -> 리에종 (결과 해석을 위해 복귀)
    workflow.add_edge("tools", "liaison")

    # 케어팀 -> 수석 집사
    workflow.add_edge("care", "head_butler")

    return workflow.compile(checkpointer=memory)


# 앱 인스턴스 생성 및 내보내기
app = create_zipsa_graph()
