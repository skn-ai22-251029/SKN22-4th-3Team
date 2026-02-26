from abc import ABC, abstractmethod
from typing import List
import numpy as np

class BaseEmbedder(ABC):
    def __init__(self, dimension: int):
        self.dimension = dimension

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """단일 쿼리 문자열을 임베딩합니다."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """문서 문자열 리스트를 임베딩합니다."""
        pass

    def validate_and_format(self, vector: List[float]) -> List[float]:
        """
        벡터가 float 리스트인지, 예상 차원과 일치하는지 확인하고,
        null 또는 빈 케이스를 처리합니다.
        """
        if not vector or len(vector) == 0:
            raise ValueError("임베딩 벡터가 비어있거나 null입니다.")
        
        if len(vector) != self.dimension:
            raise ValueError(f"임베딩 차원이 일치하지 않습니다: 기대치 {self.dimension}, 실제치 {len(vector)}")
        
        # MongoDB 호환성을 위해 명시적으로 float으로 캐스팅
        return [float(x) for x in vector]

    def normalize(self, vector: List[float]) -> List[float]:
        """코사인 유사도를 위한 L2 정규화."""
        arr = np.array(vector)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return vector
        return (arr / norm).tolist()
