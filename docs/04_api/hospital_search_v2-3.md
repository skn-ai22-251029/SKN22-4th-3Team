# Kakao Address Search API Specification

## Service Metadata

| Category           | Content                  | Category      | Content                                          |
| :----------------- | :----------------------- | :------------ | :----------------------------------------------- |
| **Classification** | 공공 - 지도·위치         | **Provider**  | (주)카카오                                       |
| **Department**     | Kakao Developers         | **Contact**   | [카카오 개발자 포럼](https://devtalk.kakao.com/) |
| **API Type**       | REST                     | **Format**    | JSON                                             |
| **Applications**   | -                        | **Keywords**  | 카카오맵,주소검색,도로명주소,좌표변환,로컬API    |
| **Reg Date**       | -                        | **Mod Date**  | 2026-01-29                                       |
| **Cost**           | 무료 (쿼터제)            | **Traffic**   | 일 100,000회 (무료 등급 기준)                    |
| **Review**         | 자동승인                 | **Scope**     | -                                                |
| **License**        | 카카오 API 이용약관 준수 | **Reference** | -                                                |

## Service Overview

- **Base URL**: `https://dapi.kakao.com/v2/local/search/address.json`
- **Method**: `GET`
- **Portal Link**: [Kakao Developers Local API](https://developers.kakao.com/docs/latest/ko/local/dev-guide)

특정 주소(도로명 또는 지번)를 입력하여 해당 위치의 **정확한 도로명주소** 및 위경도 좌표 정보를 조회하는 서비스입니다.

- 사용자는 `${FORMAT}` 변수 자리에 `json`을 지정하여 데이터를 수신함
- 반드시 HTTP Header에 **REST API 키**를 포함해야 인증이 완료됨
- 검색 결과 중 `road_address` 객체를 통해 한국 표준 도로명주소 데이터를 획득할 수 있음

---

## `addressSearch_v2`: 주소/도로명 실시간 조회

| Field             |   Required   | Type   | Description                                           |
| :---------------- | :----------: | :----- | :---------------------------------------------------- |
| **Authorization** | Required(\*) | string | `KakaoAK {REST_API_KEY}` 형식의 인증 헤더             |
| **query**         | Required(\*) | string | 검색을 원하는 주소 (예: 판교역로 235)                 |
| **page**          |   Optional   | int    | 결과 페이지 번호 (기본값 : 1)                         |
| **size**          |   Optional   | int    | 한 페이지에 보여질 문서의 개수 (최대 30, 기본값 : 10) |

### Response Structure (JSON)

````json
{
  "meta": {
    "total_count": "number",
    "is_end": "boolean",
    "pageable_count": "number"
  },
  "documents": [
    {
      "address_name": "전체 지번 주소 또는 전체 도로명 주소",
      "address_type": "REGION 또는 ROAD",
      "x": "경도(Longitude)",
      "y": "위도(Latitude)",
      "road_address": {
        "address_name": "전체 도로명 주소",
        "region_1depth_name": "시도 단위",
        "road_name": "도로명",
        "main_building_no": "건물 본번"
      }
    }
  ]
}
````

## `hospitalSearch_v3`: 동 단위 세분화 조회
- 카카오 정책 상 페이지 당 15개, 총 3페이지의 정보만 제공 가능
- 이를 우회하기 위해 동 단위로 정보를 세분화, 페이지 수를 다량 확보하는 방식
- 너무 복잡하다 싶으면 이건 그냥 스킵해주셔도 될듯
| Field | Required | Type | Description |
| :--- | :---: | :--- | :--- |
| **query** | Required(*) | string | {세부 동 명칭} (예: "역삼1동", "성산동") |
| **page** | Required | int | 1~3 (각 동별 데이터 최대 확보) |
| **Strategy** | - | - | 상위 행정구역(구) 대신 하위 행정구역(동)으로 쿼리 분할 실행 |

```json
{
  "request": {
    "method": "Loop[GET]",
    "step": "Administrative Dong Level",
    "params": {
      "query": "DONG_NAME + ' 동물병원'",
      "pagination": "1 to 3"
    }
  },
  "response_summary": {
    "deduplication": "Required (based on Road Address)",
    "data_points": ["place_name", "road_address_name", "phone"]
  }
}
````
