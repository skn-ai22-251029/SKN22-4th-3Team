import os
from typing import List
from openai import AsyncOpenAI
from .base import BaseEmbedder

class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "text-embedding-3-small"):
        # OpenAI text-embedding-3-small의 차원은 1536입니다.
        super().__init__(dimension=1536)
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def embed_query(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            input=[text.replace("\n", " ")],
            model=self.model_name
        )
        embedding = response.data[0].embedding
        return self.validate_and_format(self.normalize(embedding))

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embeddings.create(
            input=[t.replace("\n", " ") for t in texts],
            model=self.model_name
        )
        
        results = []
        for item in response.data:
            results.append(self.validate_and_format(self.normalize(item.embedding)))
        return results
