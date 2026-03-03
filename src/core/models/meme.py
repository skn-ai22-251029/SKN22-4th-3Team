"""
밈 분석 Pydantic 모델.
"""
from pydantic import BaseModel


class MemeAnalyzeResponse(BaseModel):
    meme_text: str
    breed_guess: str   # 품종명만 (예: "래그돌", "코리안숏헤어")
    age_guess: str     # 표시용 문자열 (예: "약 2살 추정")
    age_months: int    # 등록용 숫자 (예: 24)
    image_url: str     # /static/meme/{uuid}.jpg
