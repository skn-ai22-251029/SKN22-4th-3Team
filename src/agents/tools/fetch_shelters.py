import asyncio
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://apis.data.go.kr/1543061/abandonmentPublicService_v2"
SERVICE_KEY = os.getenv("OPENAPI_API_KEY")

async def _fetch(endpoint, params):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        data = resp.json()
        print(f"DEBUG {endpoint}:", data)
        return data

async def get_sido():
    params = {"serviceKey": SERVICE_KEY, "_type": "json", "numOfRows": "30"}
    data = await _fetch("sido_v2", params)
    return data["response"]["body"]["items"]["item"]

async def get_sigungu(upr_cd):
    params = {"serviceKey": SERVICE_KEY, "_type": "json", "upr_cd": upr_cd, "numOfRows": "100"}
    data = await _fetch("sigungu_v2", params)
    items = data["response"]["body"]["items"]
    if not items: return []
    item = items["item"]
    return [item] if isinstance(item, dict) else item

async def get_shelters(upr_cd, org_cd):
    params = {"serviceKey": SERVICE_KEY, "_type": "json", "upr_cd": upr_cd, "org_cd": org_cd, "numOfRows": "200"}
    data = await _fetch("shelter_v2", params)
    body = data["response"].get("body")
    if not body: return []
    items = body.get("items")
    if not items: return []
    item = items.get("item")
    if not item: return []
    return [item] if isinstance(item, dict) else item

async def main():
    print("Fetching regions...")
    sidos = await get_sido()
    
    all_shelters = []
    
    for sido in sidos:
        upr_cd = sido["orgCd"]
        sido_nm = sido.get("orgdownNm") or sido.get("orgNm") or "Unknown"
        print(f"Processing {sido_nm}...")
        
        sigungus = await get_sigungu(upr_cd)
        for sigungu in sigungus:
            org_cd = sigungu["orgCd"]
            sigungu_nm = sigungu.get("orgdownNm") or sigungu.get("orgNm") or "Unknown"
            
            shelters = await get_shelters(upr_cd, org_cd)
            for s in shelters:
                all_shelters.append({
                    "careNm": s["careNm"],
                    "careRegNo": s["careRegNo"],
                    "careAddr": s.get("careAddr", ""),
                    "careTel": s.get("careTel", ""),
                    "sido": sido_nm,
                    "sigungu": sigungu_nm
                })
    
    # Save the raw data first
    with open("shelter_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_shelters, f, ensure_ascii=False, indent=2)
    
    print(f"Done! Found {len(all_shelters)} shelters.")

if __name__ == "__main__":
    asyncio.run(main())
