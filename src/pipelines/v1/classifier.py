import os
import logging
from typing import List, Dict, Any, Type
from openai import AsyncOpenAI
from src.core.config import ZipsaConfig
from src.pipelines.v1.schemas import BatchResultV1

class V1Classifier:
    """
    Legacy Classifier for V1 Pipeline.
    Extracts Single Category & Basic Metadata.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        self.policy = ZipsaConfig.get_policy("v1")
        self.model = model
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_system_prompt(self) -> str:
        return f"""
        You are a cat consultant AI. Analyze articles and assign EXACTLY ONE category from: {', '.join(self.policy.categories)}.
        Extract category, keywords (3), summary (1 sentence), and potential_questions (2).
        """

    async def classify_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Code duplication from V2/Base but kept isolated as per request
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
                response_format=BatchResultV1,
                temperature=0
            )
            return [res.model_dump() for res in response.choices[0].message.parsed.results]
        except Exception as e:
            logging.error(f"[{self.policy.version}] Classification Error: {e}")
            return []
