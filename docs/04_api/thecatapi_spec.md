# TheCatAPI 명세서

이 문서는 `thecatapi-oas.yaml` (OpenAPI Spec 3.0.0)을 기반으로 작성된 TheCatAPI 명세서입니다.

## 기본 정보
- **API 버전**: 1.6.3
- **Base URL**: `http://api.thecatapi.com/v1`
- **인증**: 대부분의 요청에 API Key가 필요합니다.
  - 헤더 이름: `x-api-key`
  - 값: 발급받은 API Key

---

Click on this to get a random Image https://api.thecatapi.com/v1/images/search

Click this to get 10 random images https://api.thecatapi.com/v1/images/search?limit=10

Copy this link, add your own API Key to get 10 bengal images https://api.thecatapi.com/v1/images/search?limit=10&breed_ids=beng&api_key=REPLACE_ME

---

## 1. 이미지 (Images)

이미지 검색, 업로드, 분석 및 관리를 위한 엔드포인트입니다.

### GET `/images/search`
랜덤한 고양이 이미지를 검색하거나 조건에 맞는 이미지를 조회합니다.

**파라미터**

| 이름 | 위치 | 타입 | 필수 | 설명 |
|------|------|------|------|------|
| `limit` | Query | integer | No | 반환할 결과 수 (기본값: 1, API Key 사용 시 최대 25) |
| `page` | Query | integer | No | 결과 페이지 번호 (기본값: 0) |
| `order` | Query | string | No | 정렬 순서 (`RANDOM` (기본), `ASC`, `DESC`) |
| `has_breeds` | Query | boolean | No | 품종 데이터가 있는 이미지만 반환할지 여부 (Example: `true`) |
| `mime_types` | Query | string | No | 반환할 이미지 타입 (예: `jpg,png` 또는 `gif`) |
| `format` | Query | string | No | 응답 포맷 (`json` 또는 `src`) |
| `size` | Query | string | No | 이미지 크기 (`thumb`, `small`, `med`, `full`) |

**응답 예시**
```json
[
  {
    "id": "Hylo4Snaf",
    "url": "https://cdn.thedogapi.com/images/Hylo4Snaf.jpeg",
    "width": 1200,
    "height": 922,
    "mime_type": "image/jpeg",
    "breeds": [
      {
        "id": 235,
        "name": "Spanish Water Dog",
        "weight": "30 to 50 pounds",
        "height": "16 to 20 inches at the shoulder",
        "life_span": "12 to 15 years",
        "breed_group": "Sporting"
      }
    ],
    "categories": []
  }
]
```

### GET `/images/`
사용자가 업로드한 이미지 목록을 가져옵니다.

**파라미터**

| 이름 | 위치 | 타입 | 필수 | 설명 |
|------|------|------|------|------|
| `limit` | Query | integer | No | 반환할 이미지 수 (Example: `10`) |
| `page` | Query | integer | No | 페이지 번호 |
| `order` | Query | string | No | 정렬 순서 (`ASC` 또는 `DESC`) |

**응답 예시**
```json
[
  {
    "id": "S1bsCGxrf",
    "url": "http://78.media.tumblr.com/2bc94b9eec2d00f5d28110ba191da896/tumblr_nyled8DYKd1qg9kado1_1280.jpg",
    "width": null,
    "height": null,
    "mime_type": "image/jpeg",
    "entities": [],
    "breeds": [
      {
        "id": 3,
        "name": "Alaskan Malamute",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Alaskan_Malamute"
      }
    ],
    "animals": [],
    "categories": []
  }
]
```

### POST `/images/upload`
이미지를 업로드합니다.

**요청 본문 (multipart/form-data)**

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `file` | string (binary) | Yes | 업로드할 이미지 파일 |
| `sub_id` | string | No | 사용자 정의 ID (예: 사용자 구분용) |
| `breed_ids` | string | No | 이미지에 포함된 품종 ID (콤마로 구분) |

**응답 예시**
```json
{
  "id": "xxBaNrfM0",
  "url": "https://cdn2.thecatapi.com/images/xxBaNrfM0.jpg",
  "sub_id": "my-user-1",
  "width": 480,
  "height": 640,
  "original_filename": "bl4.jpeg",
  "pending": 0,
  "approved": 1
}
```

### GET `/images/{image_id}`
특정 이미지의 상세 정보를 조회합니다.

**응답 예시**
```json
{
  "id": "image_id_123",
  "url": "..."
}
```

### DELETE `/images/{image_id}`
업로드한 이미지를 삭제합니다.

**응답 예시**
```json
{}
```

### GET `/images/{image_id}/analysis`
이미지 분석 결과(라벨링 등)를 조회합니다.

**응답 예시**
```json
[
  {
    "labels": [
      {
        "Name": "Animal",
        "Confidence": 99.9,
        "Instances": [],
        "Parents": []
      },
      {
        "Name": "Cat",
        "Confidence": 99.9,
        "Instances": [],
        "Parents": [{"Name": "Animal"}]
      }
    ],
    "moderation_labels": [],
    "vendor": "AWS Rekognition",
    "image_id": "xxBaNrfM0",
    "created_at": "2023-10-28T17:44:36.000Z"
  }
]
```

### GET `/images/{image_id}/breeds`
특정 이미지에 태그된 품종 정보를 조회합니다.

### POST `/images/{image_id}/breeds`
이미지에 품종 정보를 태그합니다.

**요청 본문 (JSON)**
```json
{
  "breed_id": "abys"
}
```

### DELETE `/images/{image_id}/breeds/{breed_id}`
이미지에서 특정 품종 태그를 삭제합니다.

---

## 2. 품종 (Breeds)

고양이 품종 정보를 조회합니다.

### GET `/breeds`
모든 품종 목록을 조회합니다.

**파라미터**

| 이름 | 위치 | 타입 | 필수 | 설명 |
|------|------|------|------|------|
| `limit` | Query | integer | No | 결과 수 (Example: `10`) |
| `page` | Query | integer | No | 페이지 번호 (Example: `0`) |

**응답 예시**
```json
[
  {
    "weight": {"imperial": "7 - 10", "metric": "3 - 5"},
    "id": "abys",
    "name": "Abyssinian",
    "temperament": "Active, Energetic, Independent, Intelligent, Gentle",
    "origin": "Egypt",
    "country_codes": "EG",
    "country_code": "EG",
    "description": "The Abyssinian is easy to care for...",
    "life_span": "14 - 15",
    "indoor": 0,
    "alt_names": "",
    "adaptability": 5,
    "affection_level": 5,
    "child_friendly": 3,
    "dog_friendly": 4,
    "energy_level": 5,
    "grooming": 1,
    "health_issues": 2,
    "intelligence": 5,
    "shedding_level": 2,
    "social_needs": 5,
    "stranger_friendly": 5,
    "vocalisation": 1,
    "experimental": 0,
    "hairless": 0,
    "natural": 1,
    "rare": 0,
    "rex": 0,
    "suppressed_tail": 0,
    "short_legs": 0,
    "wikipedia_url": "https://en.wikipedia.org/wiki/Abyssinian_(cat)",
    "hypoallergenic": 0,
    "reference_image_id": "0XYvRd7oD",
    "image": {
      "id": "0XYvRd7oD",
      "width": 1204,
      "height": 1445,
      "url": "https://cdn2.thecatapi.com/images/0XYvRd7oD.jpg"
    }
  }
]
```

### GET `/breeds/search`
품종을 검색합니다.

**파라미터**

| 이름 | 위치 | 타입 | 필수 | 설명 |
|------|------|------|------|------|
| `q` | Query | string | No | 검색어 (예: `air`) |
| `attach_image` | Query | integer | No | `1`이면 참조 이미지 정보 포함 |

**응답 예시**
```json
[
  {
    "weight": {"imperial": "8 - 15", "metric": "4 - 7"},
    "id": "asho",
    "name": "American Shorthair",
    "description": "The American Shorthair is known for...",
    "reference_image_id": "JFPROfGtQ"
  }
]
```

### GET `/breeds/{breed_id}`
특정 품종 정보를 조회합니다.

### GET `/breeds/{breed_id}/facts` (Premium)
특정 품종에 대한 사실(Facts)을 조회합니다. 이 기능은 프리미엄 기능입니다.

**파라미터**

| 이름 | 위치 | 타입 | 필수 | 설명 |
|------|------|------|------|------|
| `limit` | Query | integer | No | 결과 수 |
| `page` | Query | integer | No | 페이지 번호 |
| `order` | Query | string | No | 정렬 (`ASC`, `DESC`, `RAND`) |

**응답 예시**
```json
[
  {
    "id": "JO85Z",
    "fact": "Ragdoll cats were first bred in the 1960s...",
    "breed_id": "ragd",
    "title": "Origin"
  }
]
```

---

## 3. 즐겨찾기 (Favourites)

사용자가 좋아하는 이미지를 저장하고 관리합니다.

### GET `/favourites`
즐겨찾기 목록을 조회합니다.

**파라미터**

| 이름 | 위치 | 타입 | 필수 | 설명 |
|------|------|------|------|------|
| `sub_id` | Query | string | No | 사용자 ID로 필터링 |
| `limit` | Query | integer | No | 결과 수 |
| `page` | Query | integer | No | 페이지 번호 |

**응답 예시**
```json
[
  {
    "id": 232413577,
    "user_id": "1ejqec",
    "image_id": "asf2",
    "sub_id": "my-user-1234",
    "created_at": "2023-10-28T17:39:28.000Z",
    "image": {}
  }
]
```

### POST `/favourites`
이미지를 즐겨찾기에 추가합니다.

**요청 본문 (JSON)**
```json
{
  "image_id": "asf2",
  "sub_id": "my-user-1234"
}
```

**응답 예시**
```json
{
  "message": "SUCCESS",
  "id": 232413577
}
```

### GET `/favourites/{favourite_id}`
특정 즐겨찾기 정보를 조회합니다.

### DELETE `/favourites/{favourite_id}`
즐겨찾기를 삭제합니다.

---

## 4. 투표 (Votes)

이미지에 대한 투표(좋아요/싫어요)를 관리합니다.

### GET `/votes`
투표 목록을 조회합니다.

***파라미터** (해당 스키마에는 명시되어 있지 않으나 일반적인 패턴 따름, Spec에는 Header Auth만 명시됨)*

**응답 예시**
```json
[
  {
    "id": 1120951,
    "image_id": "asf2",
    "sub_id": "my-user-1234",
    "created_at": "2023-10-28T17:29:28.000Z",
    "value": 1,
    "country_code": "AU",
    "image": {}
  }
]
```

### POST `/votes`
이미지에 투표합니다.

**요청 본문 (JSON)**
```json
{
  "image_id": "asf2",
  "sub_id": "my-user-1234",
  "value": 1
}
```

**응답 예시**
```json
{
  "message": "SUCCESS",
  "id": 1120951,
  "image_id": "asf2",
  "sub_id": "my-user-1234",
  "value": 1,
  "country_code": "AU"
}
```

### GET `/votes/{vote_id}`
특정 투표 정보를 조회합니다.

### DELETE `/vote/{vote_id}`
투표를 삭제합니다. (주의: 경로가 `/vote/` 입니다)

---

## 5. 사실 (Facts) (Premium)

고양이 관련 랜덤 지식을 조회합니다. 이 섹션의 기능은 **프리미엄** 기능입니다.
자세한 가격 정보는 [TheCatAPI Pricing](https://thecatapi.com/#pricing)을 참고하세요.

### GET `/facts`
랜덤한 사실을 조회합니다.

**파라미터**

| 이름 | 위치 | 타입 | 필수 | 설명 |
|------|------|------|------|------|
| `limit` | Query | string (in OAS, but likely int logic) | No | 반환할 사실 개수 |

**응답 예시**
```json
[
  {
    "id": "MBM2F",
    "fact": "Cornish Rex cats have a relatively long lifespan...",
    "breed_id": "crex",
    "title": "10. Long Lifespan"
  }
]
```

---

## 6. 웹훅 (Webhooks)

### POST `/webhooks`
웹훅을 생성합니다.

**요청 본문 (JSON)**
```json
{
  "url": "https://webhook.site/8ff",
  "events": [
    "favourite.created"
  ]
}
```

**응답 예시**
```json
{
  "app": {
    "createdAt": "2022-11-28T12:45:47.677Z",
    "id": "app_2IB0DHxPDmSMYfIO2hyPwCiVsRx",
    "name": "Charef",
    "uid": "1frbda"
  },
  "endpoint": {
    "disabled": false,
    "filterTypes": ["favourite.created"],
    "id": "ep_2IQHYL2Cxdkrqo1ukzaKTDViMhx",
    "url": "https://webhook.site/8ff"
  }
}
```
