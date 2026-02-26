from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BasePreprocessor(ABC):
    """데이터 전처리를 위한 추상 기본 클래스입니다."""
    @abstractmethod
    def run(self) -> str:
        """
        전처리 로직을 실행합니다.
        Returns:
            str: 처리된 출력 파일의 경로.
        """
        pass

class BaseEmbedder(ABC):
    """임베딩 생성을 위한 추상 기본 클래스입니다."""
    @abstractmethod
    async def run(self, input_path: str) -> str:
        """
        입력 데이터에 대한 임베딩을 생성합니다.
        Args:
            input_path (str): 전처리된 데이터 파일의 경로.
        Returns:
            str: 임베딩된 데이터 파일(pickle)의 경로.
        """
        pass

class BaseLoader(ABC):
    """데이터베이스 로드를 위한 추상 기본 클래스입니다."""
    @abstractmethod
    async def run(self, input_path: str):
        """
        임베딩된 데이터를 데이터베이스에 로드합니다.
        Args:
            input_path (str): 임베딩된 데이터 파일의 경로.
        """
        pass
