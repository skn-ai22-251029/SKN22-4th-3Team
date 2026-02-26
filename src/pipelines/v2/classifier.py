import os
import logging
from typing import List, Dict, Any, Type
from openai import AsyncOpenAI
from src.core.config import ZipsaConfig
from src.pipelines.v2.schemas import BatchResultV2

class V2Classifier:
    """
    LLM-based Classifier for V2 Pipeline (Pro).
    Extracts Category, Specialist, and Metadata.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        self.policy = ZipsaConfig.get_policy("v2")
        self.model = model
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_system_prompt(self) -> str:
        return f"""
        You are an expert cat consultant AI "Zipsa". Extract 2-layer metadata.
        Layer 1 (Topic): Select ALL relevant from: {', '.join(self.policy.categories)}.
        Layer 2 (Specialist): Select relevant from: {', '.join(self.policy.specialists)}.
        Extract summary, keywords (3-5), potential_questions (2-3), target_audience, and entities in Korean.
        """

    async def classify_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return []

        user_content = "Analyze these articles:\n\n"
        for item in items:
            uid_key = 'uid' if 'uid' in item else 'index'
            user_content += f"ID: {item.get(uid_key)}\nTitle: {item['title']}\nContent: {item.get('text', '')[:2000]}\n\n"

        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_content}
                ],
                response_format=BatchResultV2,
                temperature=0
            )
            return [res.model_dump() for res in response.choices[0].message.parsed.results]
        except Exception as e:
            logging.error(f"[{self.policy.version}] Classification Error: {e}")
            return []
