from .base import BaseEmbedder
from .openai_embedder import OpenAIEmbedder

class EmbeddingFactory:
    @staticmethod
    def get_embedder(provider: str = "openai") -> BaseEmbedder:
        if provider == "openai":
            return OpenAIEmbedder()
        raise ValueError(f"지원되지 않는 임베딩 제공자입니다: {provider}")
