from typing import List
from sentence_transformers import SentenceTransformer
from .base import BaseEmbedder
import asyncio

class LocalEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "dragonkue/multilingual-e5-small-ko"):
        # E5-small-ko 차원은 384입니다.
        super().__init__(dimension=384)
        self.model = SentenceTransformer(model_name)
        # MPS 가속 설정 (M2 Pro 등 Mac 실리콘 지원)
        try:
            self.model.to("mps")
        except:
             # MPS를 사용할 수 없는 경우 CPU로 폴백
            pass

    async def embed_query(self, text: str) -> List[float]:
        # E5 모델은 성능 향상을 위해 'query: ' 접두사가 필요한 경우가 많습니다.
        processed_text = f"query: {text}"
        # sentence-transformers의 encode는 동기 방식이므로, 비동기 안전성을 위해 스레드 풀에서 실행
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, lambda: self.model.encode(processed_text))
        return self.validate_and_format(self.normalize(embedding.tolist()))

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        processed_texts = [f"passage: {t}" for t in texts]
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, lambda: self.model.encode(processed_texts))
        
        results = []
        for emb in embeddings:
            results.append(self.validate_and_format(self.normalize(emb.tolist())))
        return results
