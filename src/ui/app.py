import streamlit as st
import os
import sys
import asyncio
import uuid
import logging
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# uvloop이 활성화된 환경에서는 nest_asyncio가 호환되지 않으므로
# 표준 이벤트 루프 정책으로 전환
import streamlit.components.v1 as components
try:
    import uvloop
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
except ImportError:
    pass

# --------------- 경로 및 환경 설정 ---------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

from dotenv import load_dotenv
dotenv_path = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

for p in (CURRENT_DIR, PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

logger = logging.getLogger(__name__)

# Jinja2 설정 (NameError 방지를 위해 상단으로 이동)
template_dir = Path(__file__).parent / "components"
env = Environment(loader=FileSystemLoader(str(template_dir)))

# --------------- 페이지 설정 ---------------
st.set_page_config(page_title="ZIPSA", page_icon="🎩", layout="wide")

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY를 찾을 수 없습니다.")
    st.stop()

# --------------- 임포트 ---------------
from utils import get_zipsa_response_streaming
from src.core.models.user import UserDTO
from src.ui.renderers.cat_card import render_cat_cards
from src.core.models.cat_card import CatCardRecommendation
from src.ui.renderers.rag_doc import render_rag_documents
from src.ui.renderers.reasoning import render_streaming_reasoning

# --------------- 세션 초기화 ---------------
_defaults = {
    "page": "intro",
    "user_profile": None,
    "messages": [],
    "thread_id": str(uuid.uuid4()),
    "initialized": False,
    "profile_expanded": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# UI 옵션 및 매핑
HOUSING_OPTIONS = ["아파트", "주택", "원룸"]
ACTIVITY_OPTIONS = ["정적", "보통", "활동적"]
EXP_OPTIONS = ["초보", "경력", "베테랑"]
COMPANION_OPTIONS = ["어린 아이", "강아지", "혼자", "가족"]

HOUSING_MAP = {"apartment": "아파트", "house": "주택", "studio": "원룸"}
HOUSING_MAP_R = {v: k for k, v in HOUSING_MAP.items()}
ACTIVITY_MAP = {"low": "정적", "medium": "보통", "high": "활동적"}
ACTIVITY_MAP_R = {v: k for k, v in ACTIVITY_MAP.items()}
EXP_MAP = {"beginner": "초보", "intermediate": "경력", "expert": "베테랑"}
EXP_MAP_R = {v: k for k, v in EXP_MAP.items()}


# --- ZIPSA 글로벌 레이아웃 ---

profile = st.session_state.user_profile

def get_profile_summary(p):
    if not p:
        return None

    # UserDTO는 preferences 안에, UserProfile은 직접 접근
    pref = p.preferences if hasattr(p, "preferences") else p

    parts = []
    h = HOUSING_MAP.get(pref.housing, pref.housing)
    parts.append(f"🏠 거주: {h}")

    a = ACTIVITY_MAP.get(pref.activity, pref.activity)
    parts.append(f"🏃 활동량: {a}")

    e = EXP_MAP.get(pref.experience, pref.experience)
    parts.append(f"🎓 경력: {e}")

    if pref.companion:
        c = ", ".join(pref.companion)
        parts.append(f"👥 동거: {c}")

    al = "있음" if pref.allergy else "없음"
    parts.append(f"🚨 알레르기: {al}")

    return " · ".join(parts)

st.session_state.summary = get_profile_summary(profile)

# ================================================================
#  메인 레이아웃 및 스타일
# ================================================================
# lstrip()은 자바스크립트 문법을 깨트릴 수 있으므로 적용하지 않음
raw_html = env.get_template("layout_header.html").render(
    page=st.session_state.page,
    summary=st.session_state.summary,
    show_splash=not st.session_state.initialized
)

# st.html()은 v1.34+에서 지원되는 더 안전한 HTML 주입 방식임
if hasattr(st, "html"):
    st.html(raw_html)
else:
    st.markdown(raw_html, unsafe_allow_html=True)

if not st.session_state.initialized:
    import time; time.sleep(1.2)
    st.session_state.initialized = True
    st.rerun()

# ================================================================
#  인트로 페이지 — 온보딩 폼
# ================================================================
if st.session_state.page == "intro":
    onboarding_comp = components.declare_component("zipsa_onboarding", path=str(template_dir / "onboarding"))
    _, central_col, _ = st.columns([1, 4, 1])

    with central_col:
        onboarding_data = onboarding_comp()

        if onboarding_data:
            try:
                st.session_state.user_profile = UserDTO.from_dict(onboarding_data)
                st.session_state.page = "chat"
                st.rerun()
            except Exception as e:
                logger.error(f"온보딩 데이터 오류: {str(e)}")


# ================================================================
#  채팅 페이지
# ================================================================
else:
    col_chat, col_results = st.columns([3, 2], gap="medium")

    # -- 왼쪽: 채팅 내역 --
    with col_chat:
        for msg in st.session_state.messages:
            avatar = "🧑" if msg["role"] == "user" else "🎩"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # -- 오른쪽: 고양이 정보 결과 --
    with col_results:
        results_area = st.empty()
        
        with results_area.container():
            last_assistant = next(
                (m for m in reversed(st.session_state.messages) if m["role"] == "assistant"),
                None,
            )

            if last_assistant and last_assistant.get("recommendations"):
                try:
                    cards = [CatCardRecommendation(**rec) for rec in last_assistant["recommendations"]]
                    render_cat_cards(cards, height=900)
                except Exception as e:
                    logger.warning("고양이 카드 렌더링 실패: %s", e)
            
            # RAG 출처 문서 렌더링 (범용)
            if last_assistant:
                rag_docs = last_assistant.get("rag_docs", [])
                if rag_docs:
                    render_rag_documents(rag_docs, height=450)
            
            # 추천 정보나 RAG 문서가 없을 경우 플레이스홀더 표시
            if not last_assistant or (not last_assistant.get("recommendations") and not last_assistant.get("rag_docs")):
                chat_elements = env.get_template("chat_elements.html")
                st.markdown(chat_elements.render(state="placeholder"), unsafe_allow_html=True)

    # ---- 채팅 입력 ----
    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with col_chat:
            with st.chat_message("user", avatar="🧑"):
                st.write(prompt)

            # 새 요청 시작 시 결과 영역 초기화 (로딩 표시)
            chat_elements = env.get_template("chat_elements.html")
            results_area.markdown(chat_elements.render(state="loading"), unsafe_allow_html=True)

            with st.chat_message("assistant", avatar="🎩"):
                try:
                    # 모듈화된 스트리밍 렌더러 사용
                    response_text, metadata = render_streaming_reasoning(
                        get_zipsa_response_streaming(
                            prompt,
                            st.session_state.user_profile,
                            st.session_state.messages,
                            st.session_state.thread_id,
                        )
                    )

                    if response_text:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "recommendations": metadata.get("recommendations"),
                            "rag_docs": metadata.get("rag_docs"),
                        })
                        st.rerun()

                except Exception as e:
                    st.error(f"오류 발생: {str(e)} 😭")
