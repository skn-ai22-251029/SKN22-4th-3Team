# Abandoned Animal Information Service API Specification (V2)

## Service Metadata
| Category | Content | Category | Content |
| :--- | :--- | :--- | :--- |
| **Classification** | 농림 - 농업·농촌 | **Provider** | 농림축산식품부 농림축산검역본부 |
| **Department** | 동식물빅데이터팀 | **Contact** | 054-912-0379 |
| **API Type** | REST | **Format** | JSON+XML |
| **Applications** | 3503 | **Keywords** | 국가동물보호정보시스템,구조동물,조회,API,반려동물 |
| **Reg Date** | 2022-02-11 | **Mod Date** | 2026-01-23 |
| **Cost** | 무료 | **Traffic** | 개발계정 : 10,000 / 운영계정 : 활용사례 등록시 신청하면 트래픽 증가 가능 |
| **Review** | 개발단계 : 자동승인 / 운영단계 : 자동승인 | **Scope** | - |
| **License** | 이용허락범위 제한 없음 | **Reference** | - |

## Service Overview
- **Base URL**: `http://apis.data.go.kr/1543061/abandonmentPublicService_v2`
- **Method**: `GET` (All APIs)
- **Portal Link**: [Data Portal](https://www.data.go.kr/data/15098931/openapi.do#/)

국가동물보호정보시스템의 구조동물 정보를 조회할 수 있는 서비스이며, 구조동물정보에 포함되는 부가적인 정보를 조회할 수 있도록 시도 조회 API, 시군구 조회 API, 보호소 조회 API, 품종 조회 API를 함께 제공합니다.

- 본 데이터는 국가동물보호정보시스템을 통해 제공되는 구조동물 조회 서비스임
- 전국 시도 및 시군구 단위로 구조동물 정보를 검색할 수 있도록 API 를 제공함
- 지자체 및 관계 기관은 이를 활용하여 유실·유기 동물 관리, 정책 수립, 자원 배분 등에 근거자료로 활용할 수 있음

---

## `abandonmentPublic_v2`: 구조동물 조회
| Field | Required | Type | Description |
| :--- | :---: | :--- | :--- |
| **serviceKey** | Required(*) | string | 공공데이터포털에서 발급받은 인증키 |
| **bgnde** | Optional | string | 구조날짜(검색 시작일)(YYYYMMDD) |
| **endde** | Optional | string | 구조날짜(검색 종료일)(YYYYMMDD) |
| **upkind** | Optional | string | 축종코드 (개 : 417000, 고양이 : 422400, 기타 : 429900) |
| **kind** | Optional | string | 품종코드 (품종 조회 OPEN API 참조) |
| **upr_cd** | Optional | string | 시도코드 (시도 조회 OPEN API 참조) |
| **org_cd** | Optional | string | 시군구코드 (시군구 조회 OPEN API 참조) |
| **care_reg_no** | Optional | string | 보호소번호 (보호소 조회 OPEN API 참조) |
| **state** | Optional | string | 상태(전체 : null, 공고중 : notice, 보호중 : protect) |
| **neuter_yn** | Optional | string | 상태 (전체 : null, 예 : Y, 아니오 : N, 미상 : U) |
| **pageNo** | Optional | string | 페이지 번호 (기본값 : 1) |
| **numOfRows** | Optional | string | 페이지당 보여줄 개수 (1,000 이하), 기본값 : 10 |
| **_type** | Optional | string | xml(기본값) 또는 json |
| **bgupd** | Optional | string | 수정날짜(검색 시작일)(YYYYMMDD) |
| **enupd** | Optional | string | 수정날짜(검색 종료일)(YYYYMMDD) |
| **sex_cd** | Optional | string | 성별 (전체 : null, 수컷 : M, 암컷 : F, 미상 : Q) |
| **rfid_cd** | Optional | string | 동물등록번호(RFID 번호) |
| **desertion_no** | Optional | string | 유기번호 |
| **notice_no** | Optional | string | 공고번호 |

```json
{
  "header": {
    "reqNo": "string",
    "resultCode": "string",
    "resultMsg": "string",
    "errorMsg": "string"
  },
  "body": {
    "items": {
      "item": {
        "noticeNo": "string",
        "srvcTxt": "string",
        "popfile4": "string",
        "sprtEDate": "string",
        "desertionNo": "string",
        "rfidCd": "string",
        "happenDt": "string",
        "happenPlace": "string",
        "kindCd": "string",
        "colorCd": "string",
        "age": "string",
        "weight": "string",
        "evntImg": "string",
        "updTm": "string",
        "endReason": "string",
        "careRegNo": "string",
        "noticeSdt": "string",
        "noticeEdt": "string",
        "popfile1": "string",
        "processState": "string",
        "sexCd": "string",
        "neuterYn": "string",
        "specialMark": "string",
        "careNm": "string",
        "careTel": "string",
        "careAddr": "string",
        "orgNm": "string",
        "sfeSoci": "string",
        "sfeHealth": "string",
        "etcBigo": "string",
        "kindFullNm": "string",
        "upKindCd": "string",
        "upKindNm": "string",
        "kindNm": "string",
        "popfile2": "string",
        "popfile3": "string",
        "popfile5": "string",
        "popfile6": "string",
        "popfile7": "string",
        "popfile8": "string",
        "careOwnerNm": "string",
        "vaccinationChk": "string",
        "healthChk": "string",
        "adptnTitle": "string",
        "adptnSDate": "string",
        "adptnEDate": "string",
        "adptnConditionLimitTxt": "string",
        "adptnTxt": "string",
        "adptnImg": "string",
        "sprtTitle": "string",
        "sprtSDate": "string",
        "sprtConditionLimitTxt": "string",
        "sprtTxt": "string",
        "sprtImg": "string",
        "srvcTitle": "string",
        "srvcSDate": "string",
        "srvcEDate": "string",
        "srvcConditionLimitTxt": "string",
        "srvcImg": "string",
        "evntTitle": "string",
        "evntSDate": "string",
        "evntEDate": "string",
        "evntConditionLimitTxt": "string",
        "evntTxt": "string"
      }
    },
    "numOfRows": "string",
    "pageNo": "string",
    "totalCount": "string"
  }
}
```
---

## `sigungu_v2`: 시군구 조회
| Field | Required | Type | Description |
| :--- | :---: | :--- | :--- |
| **serviceKey** | Required(*) | string | 공공데이터포털에서 발급받은 인증키 |
| **upr_cd** | Required(*) | string | 시군구 상위코드(시도코드) (입력 시 데이터 O, 미입력 시 데이터 X) |
| **_type** | Optional | string | xml(기본값) 또는 json |
| **numOfRows** | Optional | string | 한 페이지 결과 수(1,000 이하) |
| **pageNo** | Optional | string | 페이지 번호 |

```json
{
  "header": {
    "errorMsg": "string",
    "reqNo": "string",
    "resultCode": "string",
    "resultMsg": "string"
  },
  "body": {
    "pageNo": "string",
    "items": {
      "item": {
        "orgCd": "string",
        "orgdownNm": "string",
        "uprCd": "string"
      }
    },
    "totalCount": "string",
    "numOfRows": "string"
  }
}
```
---

## `sido_v2`: 시도 조회
| Field | Required | Type | Description |
| :--- | :---: | :--- | :--- |
| **serviceKey** | Required(*) | string | 공공데이터포털에서 발급받은 인증키 |
| **numOfRows** | Optional | string | 한 페이지 결과 수(1,000 이하) |
| **pageNo** | Optional | string | 페이지 번호 |
| **_type** | Optional | string | xml(기본값) 또는 json |

```json
{
  "header": {
    "reqNo": "string",
    "resultCode": "string",
    "resultMsg": "string",
    "errorMsg": "string"
  },
  "body": {
    "items": {
      "item": {
        "orgCd": "string",
        "orgdownNm": "string"
      }
    },
    "numOfRows": "string",
    "pageNo": "string",
    "totalCount": "string"
  }
}
```
---

## `shelter_v2`: 보호소 조회
| Field | Required | Type | Description |
| :--- | :---: | :--- | :--- |
| **serviceKey** | Required(*) | string | 공공데이터포털에서 발급받은 인증키 |
| **upr_cd** | Required(*) | string | 시도코드(입력 시 데이터 O, 미입력 시 데이터 X) |
| **org_cd** | Required(*) | string | 시군구코드(입력 시 데이터 O, 미입력 시 데이터 X) |
| **_type** | Optional | string | xml(기본값) 또는 json |
| **numOfRows** | Optional | string | 한 페이지 결과 수(1,000 이하) |
| **pageNo** | Optional | string | 페이지 번호 |

```json
{
  "header": {
    "errorMsg": "string",
    "reqNo": "string",
    "resultCode": "string",
    "resultMsg": "string"
  },
  "body": {
    "pageNo": "string",
    "items": {
      "item": {
        "careNm": "string",
        "careRegNo": "string"
      }
    },
    "totalCount": "string",
    "numOfRows": "string"
  }
}
```
---

## `kind_v2`: 품종 조회
| Field | Required | Type | Description |
| :--- | :---: | :--- | :--- |
| **serviceKey** | Required(*) | string | 공공데이터포털에서 발급받은 인증키 |
| **up_kind_cd** | Required(*) | string | 축종코드 (개 : 417000, 고양이 : 422400, 기타 : 429900) |
| **_type** | Optional | string | xml(기본값) 또는 json |
| **numOfRows** | Optional | string | 한 페이지 결과 수 (1,000 이하) |
| **pageNo** | Optional | string | 페이지 번호 |

```json
{
  "header": {
    "errorMsg": "string",
    "reqNo": "string",
    "resultCode": "string",
    "resultMsg": "string"
  },
  "body": {
    "pageNo": "string",
    "items": {
      "item": {
        "kindNm": "string",
        "kindCd": "string"
      }
    },
    "totalCount": "string",
    "numOfRows": "string"
  }
}
```