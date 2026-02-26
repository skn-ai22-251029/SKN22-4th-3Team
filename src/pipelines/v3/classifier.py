import os
import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
from src.core.config import ZipsaConfig
from src.pipelines.v3.schemas import BatchResultV3

class V3Classifier:
    """
    V3 클린 파이프라인을 위한 새로운 분류기입니다.
    V3 분류 체계에 엄격하게 매핑되며 고정밀 메타데이터를 추출합니다.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        self.policy = ZipsaConfig.get_policy("v3")
        self.model = model
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_system_prompt(self) -> str:
        categories = ", ".join(self.policy.categories)
        specialists = ", ".join(self.policy.specialists)
        return f"""
        당신은 고양이 케어 도메인 전문가입니다. 제공된 기사를 분석하고 메타데이터를 추출하세요.
        
        카테고리 목록:
        {categories}
        
        전문가 목록:
        {specialists}
        
        가이드라인:
        1. title_refined: 검색 쿼리에 도움이 되도록 제목을 간결하고 유익하게 수정하세요.
        2. categories: 목록에서 가장 관련 있는 카테고리를 1~3개 선택하세요.
        3. specialists: 가장 적합한 페르소나를 선택하세요.
        4. intent_tags: 감정적/기능적 의도 (예: '건강 알림', '초보 집사 가이드', '전문가 팁').
        5. summary: 전문적인 한국어로 된 정확히 한 문장의 요약을 작성하세요.
        """

    async def classify_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return []

        user_content = "V3 데이터베이스 입고를 위해 다음 기사들을 분석하세요:\n\n"
        for item in items:
            user_content += f"원본 제목: {item['title']}\n본문: {item.get('content', '')[:1500]}\n\n"

        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_content}
                ],
                response_format=BatchResultV3,
                temperature=0
            )
            # 필요한 경우 원본 데이터(URL 등)와 병합
            results = response.choices[0].message.parsed.results
            return [res.model_dump() for res in results]
        except Exception as e:
            logging.error(f"[V3] 분류 오류: {e}")
            return []
