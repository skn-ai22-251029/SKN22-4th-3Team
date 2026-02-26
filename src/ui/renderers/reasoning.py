"""
추론 과정 스트리밍 컴포넌트 (Streamlit).
"""
import streamlit as st
from typing import AsyncGenerator, Dict, Any
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import asyncio

# Jinja2 설정 (components 디렉토리 참조)
template_dir = Path(__file__).parent.parent / "components"
env = Environment(loader=FileSystemLoader(str(template_dir)), lstrip_blocks=True, trim_blocks=True)

def render_streaming_reasoning(stream_generator: AsyncGenerator[Dict[str, Any], None]):
    """커스텀 HTML 스타일로 에이전트 추론 과정을 실시간 렌더링."""
    reasoning_placeholder = st.empty()
    response_placeholder = st.empty()
    
    reasoning_text = ""
    response_text = ""
    metadata = {}
    
    template = env.get_template("reasoning_view.html")
    
    async def _consume_stream():
        nonlocal reasoning_text, response_text, metadata
        async for event in stream_generator:
            event_type = event.get("type")
            content = event.get("content", "")
            
            if event_type == "reasoning":
                reasoning_text += content
                html = template.render(content=reasoning_text, streaming=True)
                reasoning_placeholder.markdown(html, unsafe_allow_html=True)
            
            elif event_type == "response":
                response_text += content
                response_placeholder.markdown(
                    f"{response_text}<span class='reasoning-cursor'>▌</span>",
                    unsafe_allow_html=True
                )
            
            elif event_type == "complete":
                metadata = event.get("metadata", {})
                if reasoning_text:
                    html = template.render(content=reasoning_text, streaming=False)
                    reasoning_placeholder.markdown(html, unsafe_allow_html=True)
                response_placeholder.markdown(response_text)
            
            elif event_type == "error":
                st.error(content)
                return None, {}
        return response_text, metadata

    return asyncio.run(_consume_stream())
