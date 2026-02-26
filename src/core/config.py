import os
from dataclasses import dataclass
from typing import List, Dict, Any, Literal

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

# V1 레거시 정책
V1_POLICY = VersionPolicy(
    version="v1",
    db_name="catfit",
    processed_data_path="data/v1/bemypet_catlab_preprocessed.json",
    breed_data_path="data/v1/cat_breeds_integrated.json",
    is_multi_label=False,
    has_specialists=False,
    categories=["Health", "Nutrition", "Behavior", "Care", "Grooming", "Product", "General"]
)

# V2 프로 정책
V2_POLICY = VersionPolicy(
    version="v2",
    db_name="catfit_v2",
    processed_data_path="data/v2/bemypet_catlab_v2_preprocessed.json",
    breed_data_path="data/v2/cat_breeds_integrated.json",
    is_multi_label=True,
    has_specialists=True,
    categories=[
        "Health (건강/질병)", "Nutrition (영양/식단)", "Behavior (행동/심리)",
        "Care (양육/관리)", "Living (생활/환경)", "Product (제품/용품)",
        "Legal/Social (법률/사회)", "Farewell (이별/상실)", "General Info (상식/정보)"
    ],
    specialists=[
        "Matchmaker (맞춤 추천)", "Liaison (실전 입양/구조)",
        "Peacekeeper (갈등 조정/행동)", "Physician (건강/의료)"
    ]
)

# V3 클린 정책
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
    POLICIES = {
        "v1": V1_POLICY,
        "v2": V2_POLICY,
        "v3": V3_POLICY
    }

    @classmethod
    def get_policy(cls, version: str) -> VersionPolicy:
        if version not in cls.POLICIES:
            raise ValueError(f"알 수 없는 버전입니다: {version}")
        return cls.POLICIES[version]

class LLMConfig:
    # 기본 분류/라우팅용 (속도/비용 최적화)
    ROUTER_MODEL = "gpt-4.1-nano"
    
    # 요약/추출/일반대화용 (단순 작업)
    BASIC_MODEL = "gpt-4o-mini"

