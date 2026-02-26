import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


class MongoDBManager:
    """
    MongoDB 연결을 중앙에서 관리하는 매니저 클래스입니다.
    V1 (레거시), V2 (프로), V3 클러스터를 모두 지원합니다.
    """
    
    @staticmethod
    def get_v1_client():
        uri = os.getenv("MONGO_V1_URI") or os.getenv("MONGO_URI")
        if not uri:
            raise ValueError(".env 파일에서 MONGO_V1_URI 또는 MONGO_URI를 찾을 수 없습니다.")
        return AsyncIOMotorClient(uri, tlsCAFile=certifi.where())

    @staticmethod
    def get_v2_client():
        uri = os.getenv("MONGO_V2_URI")
        if not uri:
            raise ValueError(".env 파일에서 MONGO_V2_URI를 찾을 수 없습니다.")
        return AsyncIOMotorClient(uri, tlsCAFile=certifi.where())

    @staticmethod
    def get_v1_db():
        from src.core.config import ZipsaConfig
        client = MongoDBManager.get_v1_client()
        return client[ZipsaConfig.get_policy("v1").db_name]

    @staticmethod
    def get_v2_db():
        from src.core.config import ZipsaConfig
        client = MongoDBManager.get_v2_client()
        return client[ZipsaConfig.get_policy("v2").db_name]

    @staticmethod
    def get_v1_index_config():
        return {
            "name": "vector_index",
            "definition": {
                "fields": [
                    {"numDimensions": 1536, "path": "embedding", "similarity": "cosine", "type": "vector"},
                    {"path": "category", "type": "filter"}
                ]
            }
        }

    @staticmethod
    def get_v2_index_config():
        return {
            "name": "vector_index",
            "definition": {
                "fields": [
                    {"numDimensions": 1536, "path": "embedding", "similarity": "cosine", "type": "vector"},
                    {"path": "categories", "type": "filter"},
                    {"path": "specialists", "type": "filter"}
                ]
            }
        }

    @staticmethod
    def get_v3_client():
        uri = os.getenv("MONGO_V3_URI")
        if not uri:
            # V3 URI가 명시적으로 설정되지 않은 경우 V2 URI를 사용 (동일 클러스터로 가정)
            uri = os.getenv("MONGO_V2_URI")
            if not uri:
                 raise ValueError(".env 파일에서 MONGO_V3_URI 또는 MONGO_V2_URI를 찾을 수 없습니다.")
        return AsyncIOMotorClient(uri, tlsCAFile=certifi.where())

    @staticmethod
    def get_v3_db():
        from src.core.config import ZipsaConfig
        client = MongoDBManager.get_v3_client()
        return client[ZipsaConfig.get_policy("v3").db_name]

    @staticmethod
    def get_v3_index_config():
        return {
            "name": "vector_index",
            "definition": {
                "fields": [
                    {"numDimensions": 1536, "path": "embedding", "similarity": "cosine", "type": "vector"},
                    {"path": "categories", "type": "filter"},
                    {"path": "specialists", "type": "filter"},
                    # [메타데이터 필터] 품종 통계를 위한 숫자 필터
                    {"path": "filter_shedding", "type": "filter"},
                    {"path": "filter_energy", "type": "filter"},
                    {"path": "filter_intelligence", "type": "filter"},
                    {"path": "filter_affection", "type": "filter"},
                    {"path": "filter_child_friendly", "type": "filter"},
                    {"path": "filter_indoor", "type": "filter"},
                    {"path": "filter_lap", "type": "filter"},
                    {"path": "filter_hypoallergenic", "type": "filter"},
                    {"path": "filter_adaptability", "type": "filter"},
                    {"path": "filter_dog_friendly", "type": "filter"},
                    {"path": "filter_grooming", "type": "filter"},
                    {"path": "filter_health_issues", "type": "filter"},
                    {"path": "filter_social_needs", "type": "filter"},
                    {"path": "filter_stranger_friendly", "type": "filter"},
                    {"path": "filter_vocalisation", "type": "filter"}
                ]
            }
        }
