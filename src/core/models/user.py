from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.core.models.user_profile import UserProfile


class UserDTO(BaseModel):
    """
    통합 유저 DTO.

    인증 레이어(NextAuth)의 식별 정보와 온보딩 선호 데이터(UserProfile)를 통합합니다.
    - user_id, email, nickname: 인증/DB 식별자 (인증 미구현 시 None)
    - preferences: 온보딩에서 수집한 사용자 환경 및 선호 조건
    """
    # 인증 식별자 (NextAuth users 컬렉션)
    user_id: Optional[str] = Field(default=None, description="MongoDB users._id (문자열)")
    email: Optional[str] = Field(default=None, description="OAuth 이메일")

    # 유저 프로필 (user_profiles 컬렉션 최상위 필드)
    nickname: Optional[str] = Field(default=None, description="닉네임")
    age: Optional[int] = Field(default=None, description="나이")
    gender: Optional[str] = Field(default=None, description="성별 (M | F | 미설정)")
    contact: Optional[str] = Field(default=None, description="연락처")
    address: Optional[str] = Field(default=None, description="주소")

    preferences: UserProfile = Field(
        default_factory=UserProfile,
        description="온보딩 선호 데이터 (구 UserProfile)"
    )

    def to_context_string(self) -> str:
        """LLM 컨텍스트용 문자열. preferences에 위임합니다."""
        return self.preferences.to_context_string()

    def get_hard_constraints(self) -> Dict[str, int]:
        """안전 필수 MongoDB 필터 조건. preferences에 위임합니다."""
        return self.preferences.get_hard_constraints()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserDTO":
        """온보딩 폼 dict에서 UserDTO를 생성합니다."""
        return cls(preferences=UserProfile.from_dict(data))

    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "UserDTO":
        """AgentState의 user_profile 필드에서 UserDTO를 복원합니다."""
        profile_data = state.get("user_profile", {})
        if isinstance(profile_data, UserDTO):
            return profile_data
        if isinstance(profile_data, UserProfile):
            return cls(preferences=profile_data)
        # 직렬화된 UserDTO dict (preferences 키 포함) → model_validate로 복원
        if isinstance(profile_data, dict) and "preferences" in profile_data:
            return cls.model_validate(profile_data)
        # 온보딩 flat dict 포맷
        return cls.from_dict(profile_data)
