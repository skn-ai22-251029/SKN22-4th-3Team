# 📊 ZIPSA KPI & Evaluation Metrics (Simplified)

프로젝트의 성과 및 AI 에이전트의 품질을 실용적으로 측정하기 위한 **핵심 필수 지표(KPI) 정의서**입니다.
복잡한 자동 평가보다는, **시스템의 안정성(속도/에러)과 실제 유저 만족도**를 최우선으로 모니터링합니다.

---

## 1. Performance Metrics (시스템 성능 및 안정성)
시스템이 얼마나 빠르고 정확하게, 에러 없이 응답하는지를 측정하는 최우선 지표입니다.

| Metric | Definition | Target Goal | Measurement |
| :--- | :--- | :--- | :--- |
| **E2E Latency** | 사용자 질문 접수 후, 최종 답변이 UI에 렌더링 완료되기까지 걸리는 총 소요 시간. | Avg < 5s | 로그 타임스탬프 (또는 LangSmith API 소요 시간) |
| **Error Rate** | 전체 요청 중 시스템 에러(500)나 LLM 연결 타임아웃이 발생한 비율. | < 1% | Server Error Log Count / Total Requests |
| **Routing Accuracy** | 사용자의 의도를 파악하여 올바른 에이전트(`Liaison`/`Matchmaker`)로 연결한 정확도. | > 95% | (Phase 3) LangSmith 오프라인 평가(Evaluator) |

---

## 2. Cost Control Metrics (비용 통제)
프롬프트가 비대해지거나 예기치 않은 토큰 낭비를 방어하기 위한 감시 지표입니다.

| Metric | Definition | Target Goal | Measurement |
| :--- | :--- | :--- | :--- |
| **Token Usage** | 대화 한 턴(Turn)당 소비되는 평균 Input/Output 토큰 수. | **초기 측정된 기본 베이스라인(Baseline) + 20% 이내 유지** | LangSmith Usage Stats |

*   **측정 가이드:** 
    *   초기 알파 테스트 시나리오를 통해 RAG 검색 결과 텍스트와 시스템 프롬프트가 합쳐진 **기본 토큰량(Baseline)**을 먼저 측정합니다.
    *   이후 운영 중에 평균 사용량이 **Baseline 대비 20% 이상 급등(Anomaly)**하는 경우 경고로 간주합니다.
    *   이는 주로 대화 히스토리(Memory) 누적이나 너무 많은/큰 RAG 검색 결과 주입으로 인해 발생하는 "문맥 과부하(Context Overload)"를 감지하고 수정하기 위함입니다.

---

## 3. User Experience Metrics (사용자 경험)
실제 서비스를 사용하는 유저가 체감하는 챗봇의 품질입니다.

| Metric | Definition | Measurement |
| :--- | :--- | :--- |
| **Feedback Score** | 챗봇의 각 응답 하단에 달린 좋아요(👍) 및 싫어요(👎) 클릭 비율. | UI Feedback Widget Data -> LangSmith Client 전송 |

*   **구현 방향:** 복잡한 LLM-as-a-Judge 자동 품질 평가(Ragas 등) 대신, 초기에는 가장 직관적이고 정확한 **실제 유저 피드백(User Score 1.0 or 0.0)** 수집 기능 개발에 집중합니다.
*   **활용:** 싫어요(👎)를 연달아 받은 대화 세션의 로그를 추출하여 프롬프트를 개선하는 '주간 피드백 루프' 운영에 사용합니다.
