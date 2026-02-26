from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class DebugLevel(str, Enum):
    """디버깅 정보 상세도 레벨"""
    MINIMAL = "minimal"      # 사용자 UI용 (추론만)
    STANDARD = "standard"    # 기본 (추론 + 주요 메트릭)
    VERBOSE = "verbose"      # 개발자용 (모든 필드)


class SearchDebugInfo(BaseModel):
    """검색 관련 디버깅 정보"""
    query: str = Field(..., description="검색 쿼리")
    filters: Dict[str, Any] = Field(default_factory=dict, description="적용된 필터")
    retrieved_count: int = Field(default=0, description="검색된 문서 수")
    
    def to_ui_string(self) -> str:
        """UI 표시용 문자열"""
        filter_str = ', '.join(f"{k}={v}" for k, v in self.filters.items()) if self.filters else "없음"
        return f"🔍 검색: \"{self.query}\" | 필터: {filter_str} | 결과: {self.retrieved_count}건"


class NodeDebugInfo(BaseModel):
    """단일 노드 실행 정보"""
    node_name: str = Field(..., description="노드 이름 (예: Matchmaker, Head Butler)")
    node_type: str = Field(..., description="노드 타입 (router, specialist, supervisor)")
    reasoning: str = Field(..., description="LLM 추론 과정 (한글)")
    decision: Optional[str] = Field(None, description="라우팅 결정 (다음 노드명)")
    
    # 선택적 상세 정보
    search_info: Optional[SearchDebugInfo] = None
    output_count: Optional[int] = Field(None, description="생성된 추천/응답 수")
    execution_time_ms: Optional[float] = Field(None, description="실행 시간 (밀리초)")
    llm_input: Optional[List[Dict[str, Any]]] = Field(None, description="LLM 입력 메시지 (VERBOSE용)")
    llm_output: Optional[Dict[str, Any]] = Field(None, description="LLM 구조화 출력 (VERBOSE용)")
    
    def to_dict(self, level: DebugLevel = DebugLevel.STANDARD) -> Dict[str, Any]:
        """레벨별 딕셔너리 변환"""
        if level == DebugLevel.MINIMAL:
            return {"node": self.node_name, "reasoning": self.reasoning}
        elif level == DebugLevel.STANDARD:
            base = self.model_dump(exclude_none=True, exclude={"llm_input", "llm_output"})
            if self.search_info:
                base["search_summary"] = self.search_info.to_ui_string()
                del base["search_info"]
            return base
        else:  # VERBOSE
            return self.model_dump(exclude_none=True)


class AgentTrace(BaseModel):
    """전체 에이전트 실행 추적"""
    session_id: str = Field(..., description="세션 ID (thread_id)")
    nodes_executed: List[NodeDebugInfo] = Field(default_factory=list)
    loop_detected: bool = Field(default=False)
    total_execution_time_ms: Optional[float] = None
    
    def add_node_trace(self, node_info: NodeDebugInfo):
        """노드 실행 기록 추가"""
        self.nodes_executed.append(node_info)
    
    def to_timeline(self, level: DebugLevel = DebugLevel.STANDARD) -> List[Dict[str, Any]]:
        """시간순 타임라인 생성 (UI용)"""
        return [node.to_dict(level) for node in self.nodes_executed]
    
    def get_reasoning_chain(self) -> List[str]:
        """추론 체인만 추출 (UI 간단 모드)"""
        return [f"{node.node_name}: {node.reasoning}" for node in self.nodes_executed]
