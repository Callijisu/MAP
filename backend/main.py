"""
청년 정책 추천 시스템 - FastAPI 서버
Multi-Agent 협업 기반 청년 맞춤형 정책자금 추천 시스템
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
import uvicorn

# MongoDB 핸들러 및 Agent 임포트
from database.mongo_handler import get_mongodb_handler

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="청년 정책 추천 시스템 API",
    description="Multi-Agent 협업 기반 청년 맞춤형 정책자금 추천 시스템",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB 핸들러 전역 인스턴스
mongo_handler = None

# 서버 시작 시 MongoDB 초기화
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 이벤트"""
    global mongo_handler
    try:
        mongo_handler = get_mongodb_handler()
        if mongo_handler.is_connected:
            print("✅ FastAPI: MongoDB 핸들러 연결 성공")
        else:
            print("⚠️ FastAPI: MongoDB 연결 실패, 로컬 모드로 실행")
    except Exception as e:
        print(f"⚠️ FastAPI: MongoDB 초기화 실패 - {e}")

# Pydantic 모델들
class ProfileRequest(BaseModel):
    """프로필 생성 요청 모델"""
    age: int
    region: str
    income: int
    employment: str
    interest: Optional[str] = None

class ProfileResponse(BaseModel):
    """프로필 생성 응답 모델"""
    success: bool
    profile_id: str
    message: str

class PolicyItem(BaseModel):
    """정책 항목 모델"""
    id: str
    title: str
    description: str
    category: str

class RecommendRequest(BaseModel):
    """추천 요청 모델"""
    profile_id: str

class RecommendResponse(BaseModel):
    """추천 응답 모델"""
    success: bool
    profile_id: str
    recommendations: List[PolicyItem]
    message: str

class MatchRequest(BaseModel):
    """정책 매칭 요청 모델"""
    age: int
    region: str
    income: int
    employment: str
    interest: Optional[str] = None
    min_score: Optional[float] = 40.0
    max_results: Optional[int] = 10

class MatchResult(BaseModel):
    """매칭 결과 개별 정책 모델"""
    policy_id: str
    title: str
    category: str
    score: float
    match_reasons: List[str]
    benefit_summary: str
    deadline: Optional[str] = None

class MatchResponse(BaseModel):
    """정책 매칭 응답 모델"""
    success: bool
    message: str
    user_profile_summary: str
    total_matches: int
    avg_score: float
    category_distribution: Optional[Dict[str, int]] = None
    recommendations: List[MatchResult]

class ExplainRequest(BaseModel):
    """정책 설명 요청 모델"""
    age: int
    region: str
    income: int
    employment: str
    interest: Optional[str] = None
    policies: List[Dict[str, Any]]

class ExplainedPolicy(BaseModel):
    """설명이 포함된 정책 모델"""
    policy_id: str
    title: str
    category: str
    score: float
    match_reasons: List[str]
    benefit_summary: str
    deadline: Optional[str] = None
    explanation: str
    explanation_meta: Optional[Dict[str, str]] = None

class ExplainResponse(BaseModel):
    """정책 설명 응답 모델"""
    success: bool
    message: str
    user_profile_summary: str
    total_explained: int
    policies: List[ExplainedPolicy]

class OrchestratorRequest(BaseModel):
    """Orchestrator 추천 요청 모델"""
    age: int
    region: str
    income: int
    employment: str
    interest: Optional[str] = None
    min_score: Optional[float] = 40.0
    max_results: Optional[int] = 10

class OrchestratorResponse(BaseModel):
    """Orchestrator 추천 응답 모델"""
    session_id: str
    success: bool
    message: str
    processing_time: float
    steps_summary: List[Dict[str, Any]]
    recommendation_result: Optional[Dict[str, Any]] = None
    error_detail: Optional[str] = None
    generated_at: str


# 기본 엔드포인트
@app.get("/", response_model=Dict[str, Any])
async def root():
    """시스템 정보 반환"""
    return {
        "service": "청년 정책 추천 시스템",
        "version": "1.0.0",
        "description": "Multi-Agent 협업 기반 청년 맞춤형 정책자금 추천 시스템",
        "status": "running",
        "database_connected": mongo_handler.is_connected if mongo_handler else False,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "profile": "/api/profile",
            "policies": "/api/policies",
            "recommend": "/api/recommend",
            "match": "/api/match",
            "explain": "/api/explain",
            "orchestrator": "/api/orchestrator"
        }
    }

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """헬스 체크 (MongoDB 상태 포함)"""
    health_status = {
        "status": "healthy",
        "database": "disconnected",
        "timestamp": None
    }

    try:
        # MongoDB 연결 상태 확인
        if mongo_handler:
            db_status = mongo_handler.test_connection()
            if db_status.get("connected"):
                health_status["database"] = "connected"
                health_status["database_info"] = {
                    "name": db_status.get("database_name"),
                    "collections": db_status.get("collections_count"),
                    "size_mb": db_status.get("database_size_mb")
                }
            else:
                health_status["database_error"] = db_status.get("error")

        from datetime import datetime
        health_status["timestamp"] = datetime.now().isoformat()

    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)

    return health_status


# 임시 API 엔드포인트들
@app.post("/api/profile", response_model=ProfileResponse)
async def create_profile(profile_data: ProfileRequest):
    """프로필 생성 (Agent1 + MongoDB 통합)"""
    try:
        # Agent1 임포트 및 초기화 (MongoDB 사용 가능한 경우 DB 연동)
        from agents.agent1_profile import Agent1

        # MongoDB 핸들러 연결 상태에 따라 DB 사용 여부 결정
        use_database = mongo_handler is not None and mongo_handler.is_connected
        agent1 = Agent1(use_database=use_database)

        # 프로필 데이터를 딕셔너리로 변환
        user_input = profile_data.dict()

        # Agent1으로 프로필 수집, 검증 및 DB 저장
        result = agent1.collect_profile(user_input)

        if result["success"]:
            # 응답 메시지에 DB 저장 상태 포함
            message = "프로필이 성공적으로 생성되었습니다."
            if result.get("database_saved"):
                message += " (데이터베이스 저장 완료)"
            elif result.get("database_error"):
                message += f" (데이터베이스 저장 실패: {result['database_error']})"

            return ProfileResponse(
                success=True,
                profile_id=result["profile_id"],
                message=message
            )
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 생성 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/policies", response_model=List[PolicyItem])
async def get_policies(category: Optional[str] = None):
    """정책 목록 조회 (Agent2 + MongoDB 연동)"""
    try:
        # Agent2 임포트 및 초기화
        from agents.agent2_data import Agent2, PolicyFilter

        # MongoDB 연결 상태에 따라 DB 사용 여부 결정
        use_database = mongo_handler is not None and mongo_handler.is_connected
        agent2 = Agent2(use_database=use_database)

        # 필터 조건 설정
        filter_conditions = None
        if category:
            filter_conditions = PolicyFilter(category=category)

        # Agent2를 통해 정책 조회
        result = agent2.get_policies_from_db(filter_conditions)

        if result["success"]:
            policies = result["policies"]

            # PolicyItem 형식으로 변환
            policy_items = []
            for policy in policies:
                policy_items.append(PolicyItem(
                    id=policy.get("policy_id", ""),
                    title=policy.get("title", ""),
                    description=policy.get("benefit", policy.get("title", "")),  # benefit을 description으로 사용
                    category=policy.get("category", "")
                ))

            return policy_items
        else:
            # Agent2 실패 시 더미 데이터 반환
            dummy_policies = [
                PolicyItem(
                    id="policy_001",
                    title="청년 창업 지원금",
                    description="만 18~39세 청년 창업자 대상 최대 5천만원 지원",
                    category="창업"
                ),
                PolicyItem(
                    id="policy_002",
                    title="청년 주택 구입 지원",
                    description="무주택 청년 대상 주택 구입 자금 저리 대출",
                    category="주거"
                ),
                PolicyItem(
                    id="policy_003",
                    title="청년 취업 성공 패키지",
                    description="구직자 대상 취업 상담 및 훈련비 지원",
                    category="일자리"
                )
            ]

            return dummy_policies

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정책 조회 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/recommend", response_model=RecommendResponse)
async def get_recommendations(request: RecommendRequest):
    """맞춤형 정책 추천 (레거시 호환)"""
    try:
        # 임시 추천 로직 - 레거시 호환용
        recommendations = [
            PolicyItem(
                id="rec_001",
                title="맞춤형 청년 창업 지원",
                description="회원님의 프로필에 맞는 창업 지원 프로그램",
                category="창업"
            ),
            PolicyItem(
                id="rec_002",
                title="청년 금융 지원 프로그램",
                description="소득 수준에 맞는 금융 지원 서비스",
                category="금융"
            )
        ]

        return RecommendResponse(
            success=True,
            profile_id=request.profile_id,
            recommendations=recommendations,
            message="맞춤형 정책 추천이 완료되었습니다. (레거시 버전)"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 처리 중 오류가 발생했습니다: {str(e)}")


@app.post("/api/orchestrator", response_model=OrchestratorResponse)
async def orchestrator_recommendation(request: OrchestratorRequest):
    """전체 에이전트 통합 추천 (Orchestrator)"""
    try:
        # Orchestrator 임포트 및 초기화
        from orchestrator import AgentOrchestrator

        # MongoDB 연결 상태에 따라 DB 사용 여부 결정
        use_database = mongo_handler is not None and mongo_handler.is_connected
        orchestrator = AgentOrchestrator(use_database=use_database)

        # 사용자 입력을 dict로 변환
        user_input = {
            "age": request.age,
            "region": request.region,
            "income": request.income,
            "employment": request.employment,
            "interest": request.interest
        }

        # 전체 추천 프로세스 실행
        result = orchestrator.process_recommendation(
            user_input,
            min_score=request.min_score,
            max_results=request.max_results
        )

        return OrchestratorResponse(
            session_id=result["session_id"],
            success=result["success"],
            message=result["message"],
            processing_time=result["processing_time"],
            steps_summary=result["steps_summary"],
            recommendation_result=result["recommendation_result"],
            error_detail=result.get("error_detail"),
            generated_at=result["generated_at"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통합 추천 처리 중 오류가 발생했습니다: {str(e)}")


@app.post("/api/match", response_model=MatchResponse)
async def match_policies(request: MatchRequest):
    """정책 매칭 (Agent2 + Agent3 협업)"""
    try:
        # Agent2로 정책 데이터 조회
        from agents.agent2_data import Agent2
        from agents.agent3_matching import Agent3

        # MongoDB 연결 상태에 따라 DB 사용 여부 결정
        use_database = mongo_handler is not None and mongo_handler.is_connected
        agent2 = Agent2(use_database=use_database)
        agent3 = Agent3()

        # 사용자 프로필 구성
        user_profile = {
            "age": request.age,
            "region": request.region,
            "income": request.income,
            "employment": request.employment,
            "interest": request.interest
        }

        # Agent2로 정책 데이터 조회
        policies_result = agent2.get_policies_from_db()

        if not policies_result.get("success"):
            # Agent2 실패 시 더미 정책 데이터 사용
            dummy_policies = [
                {
                    "policy_id": "JOB_001",
                    "title": "청년 창업 지원금",
                    "category": "창업",
                    "target_age_min": 18,
                    "target_age_max": 39,
                    "target_regions": ["전국"],
                    "target_employment": ["구직자", "자영업"],
                    "target_income_max": 10000,
                    "benefit": "최대 5천만원 지원",
                    "budget_max": 5000,
                    "deadline": "2024년 12월 31일",
                    "application_url": "https://startup.go.kr"
                },
                {
                    "policy_id": "FIN_001",
                    "title": "청년희망적금",
                    "category": "금융",
                    "target_age_min": 19,
                    "target_age_max": 34,
                    "target_regions": ["전국"],
                    "target_employment": ["재직자", "구직자"],
                    "target_income_max": 3600,
                    "benefit": "월 10만원 적립시 정부지원금 10만원",
                    "budget_max": 240,
                    "deadline": "2024년 12월 31일",
                    "application_url": "https://finlife.or.kr"
                },
                {
                    "policy_id": "HOU_001",
                    "title": "청년 주택 지원",
                    "category": "주거",
                    "target_age_min": 19,
                    "target_age_max": 34,
                    "target_regions": ["전국"],
                    "target_employment": ["재직자", "구직자"],
                    "target_income_max": 6000,
                    "benefit": "전세자금 최대 2억원",
                    "budget_max": 20000,
                    "deadline": "연중 상시",
                    "application_url": "https://hf.go.kr"
                }
            ]
            policies_data = dummy_policies
        else:
            # DB에서 조회된 정책을 Agent3용 형식으로 변환
            policies_data = []
            for policy in policies_result.get("policies", []):
                # Agent2의 PolicySummary를 Agent3용 정책 데이터로 변환
                policy_data = {
                    "policy_id": policy.get("policy_id"),
                    "title": policy.get("title"),
                    "category": policy.get("category"),
                    "target_age_min": 18,  # 기본값 (실제로는 DB에서 가져와야 함)
                    "target_age_max": 39,  # 기본값
                    "target_regions": ["전국"],  # 기본값
                    "target_employment": ["구직자", "재직자"],  # 기본값
                    "target_income_max": None,  # 제한 없음
                    "benefit": policy.get("benefit", ""),
                    "budget_max": None,
                    "deadline": policy.get("deadline"),
                    "application_url": ""
                }
                policies_data.append(policy_data)

        # Agent3로 매칭 수행
        matching_results = agent3.match_policies(
            user_profile,
            policies_data,
            min_score=request.min_score,
            max_results=request.max_results
        )

        # 매칭 요약 정보 생성
        summary = agent3.get_matching_summary(user_profile, matching_results)

        # MatchResult 형식으로 변환
        match_results = []
        for result in matching_results:
            match_results.append(MatchResult(
                policy_id=result.policy_id,
                title=result.title,
                category=result.category,
                score=result.score,
                match_reasons=result.match_reasons,
                benefit_summary=result.benefit_summary,
                deadline=result.deadline
            ))

        return MatchResponse(
            success=summary.get("success", True),
            message=summary.get("message", "매칭이 완료되었습니다."),
            user_profile_summary=summary.get("user_profile_summary", ""),
            total_matches=summary.get("total_matches", len(match_results)),
            avg_score=summary.get("avg_score", 0.0),
            category_distribution=summary.get("category_distribution"),
            recommendations=match_results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정책 매칭 중 오류가 발생했습니다: {str(e)}")


@app.post("/api/explain", response_model=ExplainResponse)
async def explain_policies(request: ExplainRequest):
    """정책 설명 생성 (Agent4 + GPT-4 연동)"""
    try:
        # Agent4 임포트 및 초기화
        from agents.agent4_gpt import Agent4

        agent4 = Agent4()

        # 사용자 프로필 구성
        user_profile = {
            "age": request.age,
            "region": request.region,
            "income": request.income,
            "employment": request.employment,
            "interest": request.interest
        }

        # Agent4로 설명 생성
        explained_policies = agent4.explain_all(request.policies, user_profile)

        # ExplainedPolicy 형식으로 변환
        explained_results = []
        for policy in explained_policies:
            explained_results.append(ExplainedPolicy(
                policy_id=policy.get("policy_id", ""),
                title=policy.get("title", ""),
                category=policy.get("category", ""),
                score=policy.get("score", 0.0),
                match_reasons=policy.get("match_reasons", []),
                benefit_summary=policy.get("benefit_summary", ""),
                deadline=policy.get("deadline"),
                explanation=policy.get("explanation", "설명을 생성할 수 없습니다."),
                explanation_meta=policy.get("explanation_meta")
            ))

        # 사용자 프로필 요약
        profile_summary = f"{request.age}세, {request.region} 거주, 연소득 {request.income:,}만원, {request.employment}"
        if request.interest:
            profile_summary += f", 관심분야: {request.interest}"

        return ExplainResponse(
            success=True,
            message=f"{len(explained_results)}개 정책에 대한 설명이 생성되었습니다.",
            user_profile_summary=profile_summary,
            total_explained=len(explained_results),
            policies=explained_results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정책 설명 생성 중 오류가 발생했습니다: {str(e)}")


# 새로운 API 엔드포인트: 프로필 조회
@app.get("/api/profile/{profile_id}")
async def get_profile(profile_id: str):
    """프로필 조회 (MongoDB에서)"""
    try:
        if not mongo_handler or not mongo_handler.is_connected:
            raise HTTPException(
                status_code=503,
                detail="데이터베이스에 연결되지 않았습니다."
            )

        # Agent1을 사용해서 프로필 조회
        from agents.agent1_profile import Agent1
        agent1 = Agent1(use_database=True)

        result = agent1.get_profile_from_database(profile_id)

        if result.get("success"):
            return {
                "success": True,
                "profile": result["profile"],
                "message": "프로필 조회 완료"
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 조회 중 오류가 발생했습니다: {str(e)}")


# 서버 실행 코드
if __name__ == "__main__":
    print("🚀 청년 정책 추천 시스템 서버 시작...")
    print("📍 Swagger UI: http://localhost:8000/docs")
    print("📍 ReDoc: http://localhost:8000/redoc")
    print("📍 MongoDB 연동: Stage 3 구현 완료")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )