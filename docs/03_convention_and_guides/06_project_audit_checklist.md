# 🧠 Team Alignment & Comprehension Checklist (팀원 이해도 점검표)

이 문서는 프로젝트 리더가 **"우리 팀원들이 내가 설계한 의도를 정확히 파악하고 있는가?"** 를 확인하기 위한 인터뷰/점검 질문지입니다.
코드 리뷰 전에, 팀원들이 아래 개념들을 **"설명할 수 있는지"** 먼저 확인하세요.

---

## 1. 🏗️ Architecture (구조 이해도)
*"우리 시스템은 왜 이렇게 생겼는가?"*

*   [ ] **3-Node 구조의 이유**: 왜 에이전트를 `Head`, `Liaison`, `Matchmaker` 셋으로 나누었는가?
    *   *정답 키워드*: 책임 분리, 복잡도 관리, 도메인(유기묘 vs 품종) 특화 로직 분리.
*   [ ] **Router vs Solver**: `Head` 에이전트는 직접 답하지 않고 라우팅만 한다는 것을 아는가?
    *   *정답 키워드*: 토큰 절약, 전문가(Sub-agent) 위임.
*   [ ] **LangGraph Flow**: 그래프가 순환(Cycle)하는 구조가 아니라, 명확한 종료 조건이 있음을 이해하는가?
*   [ ] **Inter-Agent Communication (State)**: 각 에이전트끼리 어떻게 데이터를 주고받는지 설명할 수 있는가?
    *   *정답 키워드*: `AgentState` 객체 공유, `messages` 리스트 누적(Append) 방식.

## 2. 🧬 Data Flow (데이터 흐름 이해도)
*"데이터는 어떻게 흘러야 하는가?"*

*   [ ] **Why Pydantic?**: 왜 딕셔너리(`dict`) 대신 Pydantic 모델을 써야 하는지 설명할 수 있는가?
    *   *정답 키워드*: 런타임 데이터 검증(Validation), 자동완성, 휴먼 에러 방지.
*   [ ] **V3 Metadata**: `features`와 `metadata` 필드가 왜 분리되어 있는지 아는가?
    *   *정답 키워드*: 벡터 검색용(임베딩 대상) vs 필터링/정보 제공용 데이터 구분.
*   [ ] **Hybrid Retrieval Strategy**: 키워드 검색과 벡터 검색이 각각 어떤 컬럼을 타겟으로 하는지 아는가?
    *   *정답*: **Keyword** -> `features` (품종명, 태그 등), **Vector** -> `embedding` (설명, 성격 등 의미적 매칭).
*   [ ] **Structured Output**: 라우팅이나 도구 호출 시 왜 프롬프트로만 하지 않고 `with_structured_output`을 써야 하는가?
    *   *정답 키워드*: 파싱 에러 방지, **100% JSON 보장 (Schema Enforcement)**.

## 3. 🎯 Goal & Roadmap (목표 공유)
*"우리는 지금 무엇을, 왜 만들고 있는가?"*

*   [ ] **Phase 1의 핵심**: 현재(Phase 1) 우리가 집중해야 할 것이 "기능 추가"가 아니라 **"안정성 및 테스트"** 임을 인지하고 있는가?
*   [ ] **Privacy Awareness**: 왜 로그에 사용자의 전화번호나 주소가 그대로 남으면 안 되는지(PII) 아는가?
*   [ ] **Next.js & FastAPI**: 왜 Streamlit에서 벗어나 Next.js + FastAPI 구조로 가려 하는지 이유를 아는가?
    *   *정답 키워드*: 커스텀 UI 한계 극복, 운영/배포 효율성(API 분리).

## 4. 🤝 Process (협업 규칙)
*"우리는 어떻게 일하기로 약속했는가?"*

*   [ ] **Branch Strategy**: 왜 `fork`가 아니라 `team repository`에서 브랜치를 따서 작업해야 하는지 아는가?
*   [ ] **PR Rules**: PR을 올릴 때 최소한 테스트(`pytest`)는 돌려보고 올려야 함을 알고 있는가?
*   [ ] **Commit Message**: "커밋 메시지 대충 적으면 안 되는 이유"에 대해 동의하는가?

---

## 💡 Leader's Guide: How to use

1.  **Spot Check (불시 점검)**: 회의 중이나 티타임 때 가볍게 질문을 던져보세요.
    *   *"OO님, 왜 우리가 Head 에이전트를 따로 뒀었죠?"*
2.  **Onboarding (신규 합류)**: 새 팀원이 오면 이 체크리스트를 주면서 *"이 질문들에 답할 수 있게 문서를 읽어보세요"* 라고 가이드하세요.
3.  **PR Reject 사유**: 엉뚱한 설계를 가져오면 *"Architecture 이해도 항목 1번 다시 보고 오세요"* 라고 피드백하세요.
