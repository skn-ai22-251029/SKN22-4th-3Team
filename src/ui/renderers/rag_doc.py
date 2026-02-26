"""
RAG 출처 문서 렌더링 컴포넌트 (Streamlit).
"""
import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Template
from typing import List, Dict, Any
from pathlib import Path

# components 디렉토리에서 HTML 템플릿 로드
TEMPLATE_PATH = Path(__file__).parent.parent / "components" / "rag_document.html"

def render_rag_documents(docs: List[Dict[str, Any]], height: int = 400):
    """Streamlit에 Top-K RAG 출처 문서 렌더링."""
    if not docs:
        return
    
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = Template(template_content)
    rendered_html = template.render(docs=docs)
    
    components.html(rendered_html, height=height, scrolling=True)
