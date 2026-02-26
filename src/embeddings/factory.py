import os
from .base import BaseEmbedder

class EmbeddingFactory:
    @staticmethod
    def get_embedder(provider: str = None) -> BaseEmbedder:
        """
        제공자 문자열에 따라 임베더 인스턴스를 반환합니다.
        지정되지 않았거나 EMBEDDING_PROVIDER 환경 변수가 없는 경우 기본값으로 'local'을 사용합니다.
        """
        if provider is None:
            provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
            
        if provider == "openai":
            from .openai_embedder import OpenAIEmbedder
            return OpenAIEmbedder()
        elif provider == "local":
            from .local import LocalEmbedder
            return LocalEmbedder()
        else:
            raise ValueError(f"지원되지 않는 임베딩 제공자입니다: {provider}")
