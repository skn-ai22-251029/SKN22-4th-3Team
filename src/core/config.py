from dataclasses import dataclass
from typing import List

@dataclass
class VersionPolicy:
    version: str
    db_name: str
    collection_name: str = "care_guides"
    breed_collection: str = "breeds"
    raw_data_path: str = "data/raw/bemypet_catlab.json"
    processed_data_path: str = ""
    breed_data_path: str = ""
    
    # 분류 체계 설정
    is_multi_label: bool = False
    has_specialists: bool = False
    categories: List[str] = None
    specialists: List[str] = None
    user_dict_path: str = None

# V3 정책
V3_POLICY = VersionPolicy(
    version="v3",
    db_name="cat_library",
    processed_data_path="data/v3/bemypet_catlab_v3.json",
    breed_data_path="data/v3/cat_breeds_integrated.json",
    is_multi_label=True,
    has_specialists=True,
    user_dict_path="src/core/tokenizer/domain_dictionary.txt",
    categories=[
        "Health (건강/질병)", "Nutrition (영양/식단)", "Behavior (행동/심리)",
        "Care (양육/관리)", "Living (생활/환경)", "Product (제품/용품)",
        "Legal/Social (법률/사회)", "Farewell (이별/상실)", "General Info (상식/정보)"
    ],
    specialists=[
        "Matchmaker", "Liaison", "Peacekeeper", "Physician"
    ]
)

class ZipsaConfig:
    POLICY = V3_POLICY

    @classmethod
    def get_policy(cls, version: str) -> VersionPolicy:
        if version != "v3":
            raise ValueError(f"알 수 없는 버전입니다: {version}")
        return cls.POLICY

class TokenConfig:
    # 히스토리 컨텍스트 최대 토큰 (입력 제한, 최근 메시지 우선 유지)
    MAX_HISTORY_TOKENS: int = 4000
    # 턴당 최대 출력 토큰
    MAX_TOKENS_PER_TURN: int = 1000


class AuthConfig:
    # ZIPSA 자체 발급 JWT 설정
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30
    # 유저 데이터 MongoDB 데이터베이스명
    USER_DB_NAME: str = "zipsa"


class LLMConfig:
    # 기본 분류/라우팅용 (속도/비용 최적화)
    ROUTER_MODEL = "gpt-4.1-nano"
    
    # 요약/추출/일반대화용 (단순 작업)
    BASIC_MODEL = "gpt-4o-mini"

