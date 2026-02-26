"""
고양이 카드 렌더링 컴포넌트 (Streamlit).
"""
import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Template
from typing import List
from pathlib import Path
from src.core.models.cat_card import CatCardRecommendation

# components 디렉토리에서 HTML 템플릿 로드
TEMPLATE_PATH = Path(__file__).parent.parent / "components" / "cat_card.html"

def render_cat_cards(cards: List[CatCardRecommendation], height: int = 600):
    """Jinja2 템플릿을 이용하여 품종 카드를 Streamlit에 렌더링."""
    if not cards:
        st.info("아직 추천된 품종이 없습니다.")
        return
    
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = Template(template_content)
    cards_data = [card.model_dump() for card in cards]
    rendered_html = template.render(cards=cards_data)
    
    components.html(rendered_html, height=height, scrolling=True)

def render_single_cat_card(card: CatCardRecommendation):
    """단일 고양이 카드 렌더링."""
    render_cat_cards([card], height=400)
