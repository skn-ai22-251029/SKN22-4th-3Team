from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserProfile(BaseModel):
    """
    타입 안전성 및 유효성 검사를 포함한 표준화된 사용자 프로필 스키마입니다.
    UI, 에이전트, 필터링 로직 전반에서 사용됩니다.
    """
    # 주거 및 환경 (강력 제약 조건 - 안전 필수)
    housing: str = Field(default="apartment", description="주거 형태: 아파트, 단독주택, 원룸 등")
    has_children: bool = Field(default=False, description="자녀 유무 (어린이 안전 필수 사항)")
    has_dog: bool = Field(default=False, description="강아지 유무 (사회성/호환 필수 사항)")
    allergy: bool = Field(default=False, description="알레르기 유무 (저자극성 필수 사항)")
    
    # 라이프스타일 및 경험 (유연 선호 조건 - 랭킹용)
    activity: str = Field(default="low", description="활동 지수: 낮음, 보통, 높음")
    experience: str = Field(default="beginner", description="고양이 양육 경험 수준")
    work_style: Optional[str] = Field(default=None, description="집을 비우는 시간 등 근무 스타일")
    
    # 선호도 (컨텍스트 전용 - 시맨틱 검색용)
    traits: List[str] = Field(default_factory=list, description="원하는 고양이 성격 특징")
    companion: List[str] = Field(default_factory=list, description="함께 사는 구성원")
    
    def to_context_string(self) -> str:
        """
        LLM 컨텍스트 전달을 위해 프로필을 사람이 읽기 좋은 문자열로 변환합니다.
        """
        traits_str = ', '.join(self.traits) if self.traits else '미설정'
        allergy_str = "있음 (저자극성 품종 필수)" if self.allergy else "없음"
        companion_str = ', '.join(self.companion) if self.companion else '없음'
        return f"""
[사용자 환경 및 제약 조건]
- 주거: {self.housing}
- 활동량: {self.activity}
- 동거인: {companion_str}
- 알레르기: {allergy_str}
- 선호 성향: {traits_str}
""".strip()
    
    def get_hard_constraints(self) -> Dict[str, int]:
        """
        반드시 지켜져야 하는 안전 필수 제약 조건을 추출합니다.
        이는 LLM에 의존하지 않고 코드 레벨에서 보장되는 필터링 조건입니다.
        
        Returns:
            MongoDB 필터 조건 딕셔너리 (예: {"hypoallergenic": 1})
        """
        constraints = {}
        
        # 알레르기: 건강 필수 사항
        if self.allergy:
            constraints["hypoallergenic"] = 1
        
        # 자녀: 안전 필수 사항
        if self.has_children or "어린 아이" in self.companion:
            constraints["child_friendly"] = 4
        
        # 강아지: 행동 호환성 사항
        if self.has_dog or "강아지" in self.companion:
            constraints["dog_friendly"] = 4
        
        return constraints
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """
        기존 Dict 형식에서 UserProfile을 생성합니다 (하위 호환성).
        UI 온보딩 폼의 필드 매핑을 처리합니다.
        """
        # UI 필드명을 DTO 필드로 매핑
        has_children = "어린 아이" in data.get("companion", [])
        has_dog = "강아지" in data.get("companion", [])
        
        # 활동량 추출
        activity_map = {
            "정적 (독서, 영화)": "low",
            "활동적 (산책, 운동)": "medium",
            "매우 활동적": "high"
        }
        activity = activity_map.get(data.get("activity", ""), "low")
        
        # 경험 수준 추출
        exp_map = {
            "초보 집사 (처음이에요)": "beginner",
            "경력 집사 (1~2번)": "intermediate",
            "베테랑 (전문가 수준)": "expert"
        }
        experience = exp_map.get(data.get("experience", ""), "beginner")
        
        return cls(
            housing=data.get("housing", "apartment"),
            has_children=has_children,
            has_dog=has_dog,
            allergy=False,  # TODO: 온보딩 폼에 알레르기 필드 추가 필요
            activity=activity,
            experience=experience,
            work_style=data.get("work_style"),
            traits=data.get("traits", []),
            companion=data.get("companion", [])
        )
