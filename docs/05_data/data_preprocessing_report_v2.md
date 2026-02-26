# Data Preprocessing Report (V2 Pro - Current)

**Version**: `v2` (Pro Policy)
**Database**: `catfit_v2` (MongoDB Atlas)

---

## 1. Dataset Statistics

| Source | Raw Count | Processed Count | Status |
| :--- | :---: | :---: | :--- |
| **BemyPet Catlab** | 1,153 | 1,153 | ✅ Complete |
| **YouTube** | 8 | 8 | ✅ Complete |

---

## 2. Collections & Schema

### 📚 Articles Collection
- **Namespace**: `catfit_v2.care_guides`
- **Schema Definition**: `ArticleMetadataV2` (`src/domain/schemas.py`)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `uid` | `str` | Unique Identifier (e.g., `doc_0`) |
| `categories` | `List[str]` | **Multi-Label** Categories |
| `specialists` | `List[str]` | **Mapped Personas** (Matchmaker, etc.) |
| `keywords` | `List[str]` | Search Keywords (3-5) |
| `summary` | `str` | Korean Summary (1-2 sentences) |
| `potential_questions` | `List[str]` | Predicted QA questions |
| `target_audience` | `str` | e.g. "초보 집사" |
| `entities` | `List[str]` | Named Entities (Breeds, Diseases) |

### 🐈 Breeds Collection
- **Namespace**: `catfit_v2.breeds`
- **Source**: `data/v2/cat_breeds_integrated.json`

---

## 3. Taxonomy (V2 Specialist-Centric)

### Categories (Topics)
- `Health (건강/질병)`, `Nutrition (영양/식단)`, `Behavior (행동/심리)`
- `Care (양육/관리)`, `Living (생활/환경)`, `Product (제품/용품)`
- `Legal/Social (법률/사회)`, `Farewell (이별/상실)`, `General Info (상식/정보)`

### Specialists (Personas)
- **`Matchmaker`**: 맞춤 추천
- **`Liaison`**: 입양/구조
- **`Peacekeeper`**: 갈등/행동
- **`Physician`**: 건강/의료

---

## 4. Index Configuration

**Vector Index (`vector_index`)**:
```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "categories",
      "type": "filter"
    },
    {
      "path": "specialists",
      "type": "filter"
    }
  ]
}
```

**Keyword Index (`keyword_index`)**:
- **Mappings**:
  - `tokenized_text`: string (searchable)
  - `specialists`: string (filterable)
