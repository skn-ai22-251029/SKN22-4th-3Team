# Data Preprocessing Report (V1 Legacy)

**Version**: `v1` (Legacy Policy)
**Database**: `catfit` (MongoDB Atlas)

---

## 1. Dataset Statistics

| Source | Raw Count | Processed Count | Status |
| :--- | :---: | :---: | :--- |
| **BemyPet Catlab** | 1,153 | 1,153 | ✅ Complete |
| **YouTube** | 8 | 8 | ✅ Complete |

---

## 2. Collections & Schema

### 📚 Articles Collection
- **Namespace**: `catfit.care_guides` (Default)
- **Schema Definition**: `ArticleMetadataV1` (`src/domain/schemas.py`)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `uid` | `str` | Unique Identifier (e.g., `doc_0`) |
| `category` | `str` | **Single Label** Category |
| `keywords` | `List[str]` | Keywords |
| `summary` | `str` | Summary text |
| `potential_questions` | `List[str]` | Predicted user questions |

### 🐈 Breeds Collection
- **Namespace**: `catfit.cat_breeds` (or `breeds` depending on import)
- **Source**: `data/v1/cat_breeds_integrated.json`

---

## 3. Taxonomy (Legacy)
**Single-Label Categories**:
- `Health`, `Nutrition`, `Behavior`, `Care`, `Grooming`, `Product`, `General`

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
      "path": "category",
      "type": "filter"
    }
  ]
}
```
