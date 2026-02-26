# 📜 Scripts (`scripts/`)

데이터 수집(Crawl)부터 정제(Process), 검증(Validate), 그리고 검색 엔진 적재(Load)까지 이어지는 전체 데이터 파이프라인 운영을 전담하는 도구 모음입니다.

---

## 🏗️ Data Pipeline (Dual-Track Workflow)

본 프로젝트는 **아티클 처리**와 **품종 처리** 두 개의 독립 트랙을 운영합니다.

### **Track 1: Article Pipeline (V3)**
케어 가이드 아티클을 LLM 기반으로 정제하고 임베딩합니다.

1.  **Stage 1: Preprocess (`v3/run_preprocess.py`)**
    - **입력**: `data/raw/bemypet_catlab.json` (Raw Data, 1,153건)
    - **핵심 로직**: `src/pipelines/v3/preprocessor.py`
    - **기술**: **GPT-4o-mini**를 이용한 배치 분류 및 요약 추출 + **Kiwi** 기반 한국어 토큰화.
    - **결과**: `data/v3/processed.json` 생성.
2.  **Stage 2: Embed (`v3/run_embed.py`)**
    - **입력**: `data/v3/processed.json`
    - **핵심 로직**: `src/pipelines/v3/embedder.py`
    - **기술**: **OpenAI text-embedding-3-small** 사용. `asyncio.Semaphore`를 이용한 병렬 처리.
    - **결과**: `data/v3/embedded.pkl` (Pickle format) 생성.
3.  **Stage 3: Load (`v3/run_load.py`)**
    - **입력**: `data/v3/embedded.pkl`
    - **핵심 로직**: `src/pipelines/v3/loader.py`
    - **기술**: MongoDB Atlas의 `cat_library.care_guides` 컬렉션에 비동기 Upsert.
    - **결과**: 벡터 검색 인덱스 즉각 반영.

### **Track 2: Breed Pipeline (V3 + Policy)**
품종 데이터를 정책 기반 필터링과 함께 처리합니다.

- **Script**: `process_breeds_v3.py`
- **입력**: `data/v3/cat_breeds_integrated.json` (67종)
- **로직**:
  1. TheCatAPI 이미지 URL 매칭
  2. Breed Filtering Policy 준수 (`filter_shedding`, `filter_energy` 등 17개 지표)
  3. 통합 저장소(`cat_library.care_guides`)에 Upsert
- **결과**: 아티클과 품종이 단일 컬렉션에서 `categories`/`specialists`로 구분됨.

---

## 📂 디렉토리 및 개별 스크립트 명세

### 1. [crawl/](./crawl) - 데이터 수집 엔진
- `crawl_wiki.py`: Wikipedia 고양이 품종 정보를 JSON 형태로 수합.
- `crawl_thecatapi.py`: TheCatAPI를 호출하여 67종 묘종의 기본 스펙 및 이미지 정보 수집.
- `crawl_bemypet.py`: BemyPet Catlab 아티클 동적 크롤링.
- `download_images.py`: TheCatAPI 이미지를 로컬 `static/images/breeds/`에 다운로드.

### 2. [process/](./process) - 도메인 가공 및 지능화
- `build_domain_dict.py`: 서비스 특화 형태소 분석 사전(`src/core/tokenizer/domain_dictionary.txt`) 빌드.
- `process_breeds_v3.py`: 67종 묘종의 통계치와 Breed Filtering Policy를 V3 스키마에 맞춰 가공.
- `preprocess_integrated_breeds.py`: 중복된 묘종 정보 제거 및 명칭 정규화.

### 3. [validate/](./validate) - 품질 및 성능 검증
- `validate_bemypet.py` / `validate_wiki.py`: 데이터 스키마 정확도 및 필수 필드 검사.
- `generate_testset.py`: 검색 성능(Hit@3, MRR) 측정을 위한 **Golden Dataset** 생성.

### 4. Test Scripts (E2E Validation)
- `test_end_to_end_filter.py`: 동적 필터링 및 카드 생성 통합 테스트.
- `test_metadata_filter.py`: Atlas Vector Search 메타데이터 필터 검증.

---

## 🛠️ 실행 가이드 (V3 Pipeline 예시)
```bash
# [아티클 처리]
python scripts/v3/run_preprocess.py  # 전처리 및 LLM 메타데이터 추출
python scripts/v3/run_embed.py       # 비동기 병렬 임베딩 생성
python scripts/v3/run_load.py        # MongoDB Atlas 적재

# [품종 처리]
python scripts/process_breeds_v3.py  # 품종 데이터 정책 기반 가공 및 적재
```
