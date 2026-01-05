"""
MongoDB 데이터 모델 정의
청년 정책 추천 시스템의 MongoDB 저장용 Pydantic 모델들
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """MongoDB ObjectId를 Pydantic에서 사용하기 위한 커스텀 타입"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


class UserProfileDB(BaseModel):
    """
    MongoDB 저장용 사용자 프로필 모델
    Agent1에서 수집한 사용자 정보를 데이터베이스에 저장하기 위한 모델
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    profile_id: str = Field(..., description="Agent1에서 생성한 고유 프로필 ID")
    age: int = Field(..., ge=15, le=39, description="나이 (15-39세)")
    region: str = Field(..., description="거주 지역")
    income: int = Field(..., ge=0, description="연 소득 (만원)")
    employment: str = Field(..., description="고용 상태")
    interest: Optional[str] = Field(None, description="관심 분야")
    created_at: datetime = Field(default_factory=datetime.now, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정일시")
    is_active: bool = Field(default=True, description="활성 상태")

    class Config:
        """Pydantic 설정"""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "profile_id": "profile_12345678",
                "age": 28,
                "region": "서울",
                "income": 3500,
                "employment": "재직자",
                "interest": "창업",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "is_active": True
            }
        }


class PolicyDB(BaseModel):
    """
    MongoDB 저장용 정책 모델
    정부 및 지자체 청년 지원 정책 정보를 저장하기 위한 모델
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    policy_id: str = Field(..., description="정책 고유 ID")
    title: str = Field(..., description="정책명")
    description: str = Field(..., description="정책 설명")
    category: str = Field(..., description="정책 분야")
    target_age_min: int = Field(..., ge=15, description="대상 최소 나이")
    target_age_max: int = Field(..., le=39, description="대상 최대 나이")
    target_regions: List[str] = Field(default=[], description="대상 지역 목록")
    target_employment: List[str] = Field(default=[], description="대상 고용 상태")
    budget_min: Optional[int] = Field(None, description="최소 지원 금액 (만원)")
    budget_max: Optional[int] = Field(None, description="최대 지원 금액 (만원)")
    application_period: Optional[Dict[str, str]] = Field(None, description="신청 기간")
    requirements: List[str] = Field(default=[], description="신청 요건")
    documents: List[str] = Field(default=[], description="필요 서류")
    contact: Optional[Dict[str, str]] = Field(None, description="담당 부서 연락처")
    website_url: Optional[str] = Field(None, description="정책 웹사이트 URL")
    created_at: datetime = Field(default_factory=datetime.now, description="등록일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정일시")
    is_active: bool = Field(default=True, description="활성 상태")

    class Config:
        """Pydantic 설정"""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "policy_id": "policy_001",
                "title": "청년 창업 지원금",
                "description": "만 18~39세 청년 창업자 대상 최대 5천만원 지원",
                "category": "창업",
                "target_age_min": 18,
                "target_age_max": 39,
                "target_regions": ["서울", "경기", "전국"],
                "target_employment": ["구직자", "자영업"],
                "budget_min": 1000,
                "budget_max": 5000,
                "application_period": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                },
                "requirements": ["사업 계획서 제출", "멘토링 프로그램 참여"],
                "documents": ["사업자등록증", "사업계획서", "신분증"],
                "contact": {
                    "department": "청년정책과",
                    "phone": "02-123-4567",
                    "email": "youth@seoul.go.kr"
                },
                "website_url": "https://youth.seoul.go.kr/startup"
            }
        }


class RecommendationDB(BaseModel):
    """
    MongoDB 저장용 추천 이력 모델
    사용자별 정책 추천 결과와 이력을 저장하기 위한 모델
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    recommendation_id: str = Field(..., description="추천 고유 ID")
    user_profile_id: str = Field(..., description="사용자 프로필 ID")
    recommended_policies: List[Dict[str, Any]] = Field(default=[], description="추천된 정책 목록")
    recommendation_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="추천 점수")
    agent_used: str = Field(..., description="추천에 사용된 Agent 정보")
    recommendation_reason: Optional[str] = Field(None, description="추천 이유")
    user_feedback: Optional[Dict[str, Any]] = Field(None, description="사용자 피드백")
    viewed_at: Optional[datetime] = Field(None, description="사용자가 조회한 시간")
    applied_policies: List[str] = Field(default=[], description="신청한 정책 ID 목록")
    created_at: datetime = Field(default_factory=datetime.now, description="추천일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정일시")

    class Config:
        """Pydantic 설정"""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "recommendation_id": "rec_12345678",
                "user_profile_id": "profile_12345678",
                "recommended_policies": [
                    {
                        "policy_id": "policy_001",
                        "title": "청년 창업 지원금",
                        "score": 0.95,
                        "match_reason": "창업 관심 + 나이 조건 부합"
                    }
                ],
                "recommendation_score": 0.95,
                "agent_used": "Agent2-PolicyMatcher",
                "recommendation_reason": "사용자의 창업 관심사와 소득 수준에 최적화된 정책들",
                "user_feedback": {
                    "rating": 5,
                    "comment": "매우 유용했습니다"
                },
                "applied_policies": ["policy_001"]
            }
        }


class UserSessionDB(BaseModel):
    """
    사용자 세션 관리용 모델
    사용자의 상담 세션 및 진행 상태를 추적하기 위한 모델
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    session_id: str = Field(..., description="세션 고유 ID")
    user_profile_id: str = Field(..., description="사용자 프로필 ID")
    session_status: str = Field(default="active", description="세션 상태 (active, completed, expired)")
    current_step: str = Field(default="profile_collection", description="현재 진행 단계")
    agent_history: List[Dict[str, Any]] = Field(default=[], description="Agent 처리 이력")
    user_interactions: List[Dict[str, Any]] = Field(default=[], description="사용자 상호작용 이력")
    session_data: Dict[str, Any] = Field(default={}, description="세션 임시 데이터")
    started_at: datetime = Field(default_factory=datetime.now, description="세션 시작 시간")
    last_activity: datetime = Field(default_factory=datetime.now, description="마지막 활동 시간")
    completed_at: Optional[datetime] = Field(None, description="세션 완료 시간")
    expires_at: datetime = Field(..., description="세션 만료 시간")

    class Config:
        """Pydantic 설정"""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# 데이터베이스 컬렉션별 모델 매핑
COLLECTION_MODELS = {
    "user_profiles": UserProfileDB,
    "policies": PolicyDB,
    "recommendations": RecommendationDB,
    "user_sessions": UserSessionDB
}


def get_model_for_collection(collection_name: str):
    """
    컬렉션 이름에 해당하는 Pydantic 모델을 반환

    Args:
        collection_name (str): MongoDB 컬렉션 이름

    Returns:
        BaseModel: 해당 컬렉션의 Pydantic 모델 클래스

    Raises:
        ValueError: 지원하지 않는 컬렉션 이름인 경우
    """
    if collection_name not in COLLECTION_MODELS:
        raise ValueError(f"지원하지 않는 컬렉션입니다: {collection_name}")

    return COLLECTION_MODELS[collection_name]