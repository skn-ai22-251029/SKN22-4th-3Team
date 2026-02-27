# 품종 필터링 정책 (Breed Filtering Policy)

## 1. 개요

사용자의 자연어 표현에서 품종 선호 조건을 추출하여 MongoDB 필터로 적용합니다.
조건을 만족하는 품종이 부족할 경우 단계적 fallback을 적용합니다.

### 설계 방식: Hard Filter + Fallback

```
자연어 → 조건 추출 (LLM) → MongoDB Hard Filter → 후보 검색 → LLM 최종 선별
                                     ↓ 결과 < 3종
                              Fallback (단계적 완화)
```

> Soft hint 방식(프롬프트 힌트 주입)은 LLM이 조건을 무시할 수 있어 채택하지 않습니다.

---

---

## 2. 실제 데이터 분포 (67종 기준)

필터 설계의 근거가 되는 실제 stats 분포입니다.

### 2.1 단일 조건별 매칭 수

| 조건 | 매칭 수 | 비율 | 비고 |
|---|---|---|---|
| `shedding_level <= 2` | 18종 | 27% | 사용 |
| `shedding_level <= 3` | 60종 | 90% | fallback |
| `energy_level <= 3` | 26종 | 39% | 사용 ("얌전한") |
| `energy_level >= 4` | 41종 | 61% | 사용 ("활발한") |
| `energy_level <= 2` | 4종 | 6% | 너무 strict → 미사용 |
| `vocalisation <= 2` | 27종 | 40% | 사용 |
| `social_needs <= 3` | — | — | 실제 min=3이므로 최소 기준 |
| `social_needs <= 2` | 0종 | 0% | **불가** (실제 min=3) |
| `child_friendly >= 4` | 57종 | 85% | 분화 없음 → 미사용 |
| `affection_level >= 4` | 65종 | 97% | 분화 없음 → 미사용 |
| `hypoallergenic == 1` | 15종 | 22% | 사용 |
| `grooming <= 2` | 48종 | 72% | 사용 |

### 2.2 복합 조건 (AND) 매칭 수

| 조건 조합 | 매칭 수 | 비고 |
|---|---|---|
| `shedding_level <= 2` + `energy_level <= 2` | 0종 | fallback 필요 |
| `shedding_level <= 2` + `hypoallergenic == 1` | 6종 | 정상 |
| `child_friendly >= 4` + `energy_level <= 3` | 20종 | 정상 |
| `social_needs <= 2` + `grooming <= 2` | 0종 | social_needs 불가 |
| `energy_level >= 4` + `affection_level >= 4` | 41종 | affection 분화 없음 |

### 2.3 필터에서 제외하는 필드

실제 데이터 분포상 거의 모든 품종이 높은 값을 가져 필터 의미가 없는 필드:

| 필드 | 이유 |
|---|---|
| `affection_level` | 97%가 4-5 |
| `child_friendly` | 85%가 >= 4 |
| `adaptability` | 평균 4.8, 대부분 5 |
| `dog_friendly` | 평균 4.6 |

---

## 3. Stats 필드 정의 (1-5 척도)

| 필드 | 설명 | 낮음 (1-2) | 높음 (4-5) |
|---|---|---|---|
| `shedding_level` | 털 빠짐 정도 | 털 거의 안 빠짐 | 털 많이 빠짐 |
| `energy_level` | 활동성 | 얌전함, 조용함 | 활발함, 에너지 넘침 |
| `affection_level` | 애정도 | 독립적 | 애교 많음 |
| `child_friendly` | 아이 친화성 | 아이 비추 | 아이 있는 집 적합 |
| `social_needs` | 사회적 욕구 | 혼자 있어도 잘 지냄 | 혼자 두면 힘들어함 |
| `vocalisation` | 울음소리 빈도 | 조용함 | 말이 많음 |
| `grooming` | 그루밍 필요도 | 관리 쉬움 | 자주 빗질 필요 |
| `intelligence` | 지능 | — | 훈련 가능, 영리함 |
| `stranger_friendly` | 낯선 사람 친화성 | 낯을 많이 가림 | 사교적 |
| `adaptability` | 적응력 | 환경 변화에 민감 | 새 환경 잘 적응 |
| `health_issues` | 건강 문제 빈도 | 건강한 편 | 유전 질환 주의 |
| `hypoallergenic` | 저알레르기 여부 | — | 0 또는 1 |
| `lap` | 무릎냥이 여부 | — | 0 또는 1 |
| `indoor` | 실내 적합도 | — | 0 또는 1 |

---

## 4. 자연어 → 조건 매핑 예시

| 사용자 표현 | 추출 조건 |
|---|---|
| "털 안 빠지는" | `shedding_level <= 2` |
| "털 많이 빠지는 건 싫어" | `shedding_level <= 2` |
| "활발한", "에너지 넘치는" | `energy_level >= 4` |
| "얌전한", "조용한", "아파트용" | `energy_level <= 2` |
| "소리 안 내는" | `vocalisation <= 2` |
| "아이 있는 집", "아이 친화적" | `child_friendly >= 4` |
| "초보자", "처음 키우는" | `energy_level <= 3`, `grooming <= 3` |
| "애교 많은", "사람 좋아하는" | `affection_level >= 4` |
| "독립적인", "혼자 있어도 되는" | `social_needs <= 2` |
| "알레르기" | `hypoallergenic == 1` |
| "무릎냥이" | `lap == 1` |
| "영리한", "훈련 가능한" | `intelligence >= 4` |
| "그루밍 적게", "관리 쉬운" | `grooming <= 2` |

---

## 5. 적용 흐름

```
1. 사용자 발화 입력
2. extract_breed_criteria(query) → BreedCriteriaHints 추출
3. preferred_conditions가 있으면 LLM 선별 프롬프트에 [선호 조건 힌트] 섹션 추가
4. LLM은 힌트를 참고하되 전체 적합성을 종합 판단하여 최종 3종 선별
```

### Fallback 단계

| 단계 | 동작 | 프롬프트 메시지 |
|---|---|---|
| 1단계 | 전체 조건 적용, 결과 >= 3종 | — |
| 2단계 | 수치 threshold ±1 완화 | "기준을 완화하여 검색했습니다" |
| 3단계 | 바이너리 조건만 유지 (hypoallergenic, lap) | "수치 조건을 제거하고 필수 조건만 적용했습니다" |
| 4단계 | 조건 없음 | "전체 품종에서 검색합니다" |

### 선별 프롬프트 주입 예시

```
[적용된 검색 조건]
shedding_level <= 3, energy_level <= 3
※ 원하시는 조건(shedding_level <= 2, energy_level <= 2)을 모두 만족하는 품종이
  부족해 기준을 완화하여 검색했습니다.
위 조건이 반영된 후보 목록입니다. 사용자 환경과 종합하여 최적의 3종을 선별하세요.
```

---

## 6. 관련 파일

- `src/agents/filters/breed_criteria.py` — 조건 추출 모듈
- `src/agents/matchmaker.py` — 힌트 주입 연동
- `src/core/models/cat_card.py` — `CatCardStats` 필드 정의
