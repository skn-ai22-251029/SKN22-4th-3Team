"""
국가동물보호정보시스템 유기동물 조회 Tool
API: abandonmentPublicService_v2 (data.go.kr)
"""
import os
import logging

import httpx
from langchain_core.tools import tool

from .region_codes import SIDO_CODES, SIGUNGU_CODES
from .shelter_codes import SHELTER_REGISTRY

logger = logging.getLogger(__name__)

BASE_URL = "http://apis.data.go.kr/1543061/abandonmentPublicService_v2"
UPKIND_CAT = "422400"


async def _call_api(endpoint: str, params: dict) -> dict:
    """공공데이터포털 API 호출 헬퍼."""
    service_key = os.getenv("OPENAPI_API_KEY")
    if not service_key:
        raise RuntimeError("OPENAPI_API_KEY 환경변수가 설정되지 않았습니다.")
    params["serviceKey"] = service_key
    params["_type"] = "json"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{BASE_URL}/{endpoint}", params=params, timeout=30.0
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except httpx.ReadTimeout:
            logger.error(f"API 호출 타임아웃: {endpoint}")
            raise RuntimeError("공공데이터 API 서버의 응답이 너무 늦습니다. 다시 시도해 주세요.")
        except Exception as e:
            logger.error(f"API 호출 중 예외 발생: {str(e)}")
            raise


@tool
async def search_abandoned_animals(
    sido: str,
    sigungu: str = "",
    breed: str = "",
    shelter_keyword: str = "",
    state: str = "protect",
) -> dict:
    """Search for abandoned/protected cats in a given region via the national animal protection system.
    국가동물보호정보시스템에서 지역별 보호 중인 유기 고양이를 조회합니다.

    Args:
        sido: 시도명 (예: "서울특별시", "경기도")
        sigungu: 발견 장소 중심 시군구명 (예: "강남구", "수원시"). 특정 구에서 구조된 동물을 찾을 때 사용.
        breed: 품종 키워드 (예: "코리안숏헤어").
        shelter_keyword: 보호소 위치 중심 키워드 (예: "강남구", "양주시"). 특정 위치의 보호소에 있는 동물을 찾을 때 사용.
        state: 상태 필터. "notice"=공고중, "protect"=보호중. 기본값 "protect".

    Returns:
        dict with keys:
            - success: bool
            - total: int (전체 건수)
            - animals: list[dict] (최대 5건, 주요 정보)
            - message: str (에러 시 메시지)
    """
    # 시도 코드 변환
    upr_cd = SIDO_CODES.get(sido)
    if not upr_cd:
        return {
            "success": False,
            "total": 0,
            "animals": [],
            "message": f"'{sido}'에 해당하는 시도 코드를 찾을 수 없습니다. "
                       f"가능한 값: {', '.join(SIDO_CODES.keys())}",
        }

    params: dict = {
        "upkind": UPKIND_CAT,
        "upr_cd": upr_cd,
        "numOfRows": "1000",  # 보호소 키워드 필터링을 위해 충분한 데이터(최대 1000건) 확보
        "pageNo": "1",
    }

    # 시군구 코드 변환
    if sigungu:
        sigungu_map = SIGUNGU_CODES.get(upr_cd, {})
        org_cd = sigungu_map.get(sigungu)
        if not org_cd:
            return {
                "success": False,
                "total": 0,
                "animals": [],
                "message": f"'{sigungu}'에 해당하는 시군구 코드를 찾을 수 없습니다. "
                           f"가능한 값: {', '.join(sigungu_map.keys())}",
            }
        params["org_cd"] = org_cd

    # 상태 필터
    state_map = {"notice": "notice", "protect": "protect"}
    if state in state_map:
        params["state"] = state_map[state]

    try:
        resp = await _call_api("abandonmentPublic_v2", params)
    except Exception as e:
        logger.exception("유기동물 API 호출 실패")
        return {
            "success": False,
            "total": 0,
            "animals": [],
            "message": f"API 호출 중 오류가 발생했습니다: {e}",
        }

    body = resp.get("body", {})
    total = body.get("totalCount", 0)
    items = body.get("items", {})

    if not items or not items.get("item"):
        return {
            "success": True,
            "total": 0,
            "animals": [],
            "message": "조건에 맞는 보호 동물이 없습니다.",
        }

    raw_items = items["item"]
    if isinstance(raw_items, dict):
        raw_items = [raw_items]

    animals = []
    for item in raw_items:
        animal = {
            "desertionNo": item.get("desertionNo", ""),
            "breed": item.get("kindNm", item.get("kindCd", "")),
            "color": item.get("colorCd", ""),
            "age": item.get("age", ""),
            "weight": item.get("weight", ""),
            "sex": {"M": "수컷", "F": "암컷", "Q": "미상"}.get(
                item.get("sexCd", ""), "미상"
            ),
            "neuter": {"Y": "중성화 완료", "N": "미완료", "U": "미상"}.get(
                item.get("neuterYn", ""), "미상"
            ),
            "feature": item.get("specialMark", ""),
            "image": item.get("popfile1", item.get("popfile2", "")),
            "shelter_name": item.get("careNm", ""),
            "shelter_address": item.get("careAddr", ""),
            "shelter_tel": item.get("careTel", ""),
            "notice_period": f"{item.get('noticeSdt', '')}~{item.get('noticeEdt', '')}",
            "happen_place": item.get("happenPlace", ""),
        }
        
        # 품종 필터링
        if breed and breed not in animal["breed"]:
            continue
            
        # 보호소 키워드 필터링 (보호소 이름 또는 주소에 키워드가 포함된 경우)
        if shelter_keyword:
            in_name = shelter_keyword in animal["shelter_name"]
            in_addr = shelter_keyword in animal["shelter_address"]
            if not (in_name or in_addr):
                continue
            
        animals.append(animal)
        if len(animals) >= 5:
            break

    return {
        "success": True,
        "total": total,
        "animals": animals,
        "message": f"총 {total}건 중 {len(animals)}건을 표시합니다.",
    }
