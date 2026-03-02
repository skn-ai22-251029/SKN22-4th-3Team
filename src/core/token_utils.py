"""
토큰 관리 유틸리티

대화 히스토리를 max_tokens 이내로 트리밍하여
LLM 컨텍스트 초과 및 불필요한 비용을 방지한다.
"""
from typing import Any, Sequence

from langchain_core.messages import BaseMessage, trim_messages


def trim_history(
    messages: Sequence[BaseMessage],
    max_tokens: int,
    token_counter: Any,
) -> list[BaseMessage]:
    """
    대화 히스토리를 max_tokens 이내로 트리밍한다.

    Args:
        messages: 전체 대화 히스토리.
        max_tokens: 허용할 최대 토큰 수.
        token_counter: 토큰 계산에 사용할 LLM 인스턴스.

    Returns:
        최근 메시지를 우선 유지한 트리밍된 메시지 리스트.
    """
    return trim_messages(
        list(messages),
        max_tokens=max_tokens,
        strategy="last",
        token_counter=token_counter,
        include_system=False,
        allow_partial=False,
        start_on="human",
    )
