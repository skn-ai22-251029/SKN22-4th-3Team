"""
/api/v1/meme — 냥심 번역기 라우터

고양이 사진 업로드 → GPT-4o-mini Vision → 시니컬한 밈 텍스트 생성
"""
import base64
import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from openai import AsyncOpenAI

from src.api.dependencies import get_current_user
from src.core.models.auth import AuthUser
from src.core.models.meme import MemeAnalyzeResponse

router = APIRouter(prefix="/api/v1/meme", tags=["Meme"])

_STATIC_DIR = Path(__file__).parents[3] / "static" / "meme"

_VISION_SYSTEM = """당신은 도도하고 시니컬한 고양이입니다. 사진 속 고양이를 분석해 밈 텍스트를 생성하세요.
반드시 아래 JSON만 출력하세요:
{"meme_text": "...", "breed_guess": "...", "age_guess": "...", "age_months": 0}
- meme_text: 고양이 시점의 시니컬한 한 마디 (따옴표 포함, 20~60자)
- breed_guess: 추정 품종명만, 조사/문장 없이 (예: "래그돌", "코리안숏헤어", "페르시안")
- age_guess: 표시용 나이 문자열 (예: "약 2살 추정", "6개월 미만")
- age_months: 추정 나이(개월 수, 정수). 2살이면 24, 6개월이면 6"""


@router.post("/analyze", response_model=MemeAnalyzeResponse)
async def analyze_meme(
    image: UploadFile = File(...),
    context: str = Form(""),
    current_user: AuthUser = Depends(get_current_user),
) -> MemeAnalyzeResponse:
    """고양이 사진 → Vision AI → 시니컬한 밈 텍스트 생성."""
    _STATIC_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 이미지 읽기 + base64 인코딩
    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode()
    ext = Path(image.filename or "image.jpg").suffix or ".jpg"
    media_type = image.content_type or "image/jpeg"

    # 2. 파일 저장
    file_name = f"{uuid.uuid4()}{ext}"
    save_path = _STATIC_DIR / file_name
    save_path.write_bytes(image_bytes)
    image_url = f"/static/meme/{file_name}"

    # 3. GPT-4o-mini Vision 호출
    user_content: list = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{image_b64}"},
        }
    ]
    if context:
        user_content.append({"type": "text", "text": context})

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _VISION_SYSTEM},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            max_tokens=256,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Vision API 호출 실패: {e}",
        )

    raw = response.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Vision API 응답 파싱 실패",
        )

    return MemeAnalyzeResponse(
        meme_text=data.get("meme_text", "..."),
        breed_guess=data.get("breed_guess", "품종 불명"),
        age_guess=data.get("age_guess", "나이 불명"),
        age_months=int(data.get("age_months", 0)),
        image_url=image_url,
    )
