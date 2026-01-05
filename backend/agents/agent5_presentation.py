"""
Agent 5: 결과 포맷팅 및 프레젠테이션 에이전트
청년 정책 추천 시스템의 다섯 번째 에이전트로, 매칭 결과를 UI에 최적화된 형태로 포맷팅합니다.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime


class PolicyCard(BaseModel):
    """
    정책 카드 모델
    UI에 표시될 정책 카드 정보를 담는 데이터 모델
    """
    policy_id: str = Field(..., description="정책 고유 ID")
    policy_name: str = Field(..., description="정책명")
    category: str = Field(..., description="정책 분야")
    agency: str = Field(..., description="주관 기관")
    score: float = Field(..., description="매칭 점수")
    score_grade: str = Field(..., description="점수 등급 (S/A/B/C)")
    benefit: str = Field(..., description="혜택 요약")
    explanation: str = Field(..., description="맞춤 설명")
    application_url: Optional[str] = Field(None, description="신청 URL")
    deadline: Optional[str] = Field(None, description="신청 마감일")
    deadline_status: str = Field(..., description="마감일 상태 (urgent/normal/ongoing)")
    tags: List[str] = Field(default=[], description="정책 태그")

    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "JOB_001",
                "policy_name": "청년내일채움공제",
                "category": "일자리",
                "agency": "고용노동부",
                "score": 93.5,
                "score_grade": "S",
                "benefit": "2년 만기시 300만원~1200만원 지급",
                "explanation": "25세 구직자인 회원님께 완벽히 맞는 정책입니다...",
                "application_url": "https://www.work.go.kr",
                "deadline": "연중 상시",
                "deadline_status": "ongoing",
                "tags": ["일자리", "고용노동부", "구직자"]
            }
        }


class ComparisonTableRow(BaseModel):
    """비교 테이블 행 모델"""
    policy_name: str
    score: str
    benefit: str
    agency: str
    deadline: str


class ComparisonTable(BaseModel):
    """비교 테이블 모델"""
    headers: List[str]
    rows: List[ComparisonTableRow]


class FormattedResult(BaseModel):
    """
    포맷된 결과 모델
    UI에 최적화된 전체 결과 구조
    """
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="결과 메시지")
    user_profile_summary: str = Field(..., description="사용자 프로필 요약")
    total_count: int = Field(..., description="총 추천 정책 수")
    avg_score: float = Field(..., description="평균 매칭 점수")
    category_distribution: Dict[str, int] = Field(default={}, description="카테고리별 분포")
    recommendations: List[PolicyCard] = Field(default=[], description="추천 정책 카드 목록")
    comparison_table: Optional[ComparisonTable] = Field(None, description="비교 테이블")
    generated_at: str = Field(..., description="결과 생성 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "3개의 맞춤 정책을 찾았습니다.",
                "user_profile_summary": "25세, 서울 거주, 연소득 3,000만원, 구직자",
                "total_count": 3,
                "avg_score": 88.5,
                "category_distribution": {"일자리": 1, "주거": 1, "금융": 1},
                "recommendations": [],
                "comparison_table": None,
                "generated_at": "2024-01-05T10:30:00"
            }
        }


class Agent5:
    """
    Agent 5: 결과 포맷팅 및 프레젠테이션 에이전트

    주요 기능:
    - 매칭 결과를 UI 최적화된 JSON 형태로 포맷팅
    - 정책 카드 데이터 생성 (점수, 등급, 태그, 마감일 상태)
    - 비교 테이블 생성
    - 카테고리별 통계 및 분석
    """

    def __init__(self):
        """Agent5 초기화"""
        self.agent_name = "Presentation Formatting Agent"
        self.agent_version = "1.0.0"

        # 점수 등급 기준
        self.score_grades = {
            "S": {"min": 90, "label": "최적"},
            "A": {"min": 80, "label": "우수"},
            "B": {"min": 70, "label": "양호"},
            "C": {"min": 60, "label": "보통"},
            "D": {"min": 40, "label": "미흡"}
        }

    def _get_score_grade(self, score: float) -> str:
        """점수에 따른 등급 계산"""
        for grade, criteria in self.score_grades.items():
            if score >= criteria["min"]:
                return grade
        return "F"

    def _extract_agency_from_policy(self, policy: Dict[str, Any]) -> str:
        """정책에서 주관 기관 추출"""
        # 기관명 매핑
        agency_mapping = {
            "청년내일채움공제": "고용노동부",
            "청년희망적금": "금융위원회",
            "청년 주택": "국토교통부",
            "청년 전세": "국토교통부",
            "창업": "중소벤처기업부",
            "대출": "금융위원회",
            "일자리": "고용노동부"
        }

        title = policy.get("title", "")
        category = policy.get("category", "")

        # 정책명에서 기관 추출
        for keyword, agency in agency_mapping.items():
            if keyword in title:
                return agency

        # 카테고리에서 기관 추출
        for keyword, agency in agency_mapping.items():
            if keyword in category:
                return agency

        # 기본값
        return policy.get("agency", "관련 기관")

    def _analyze_deadline_status(self, deadline: Optional[str]) -> str:
        """마감일 상태 분석"""
        if not deadline:
            return "unknown"

        deadline_lower = deadline.lower()

        # 상시 모집
        if any(keyword in deadline_lower for keyword in ["상시", "연중", "수시"]):
            return "ongoing"

        # 현재 날짜 기준 분석 (실제 구현에서는 더 정교하게)
        current_month = datetime.now().month

        # 급하게 마감되는 경우
        if any(keyword in deadline_lower for keyword in [f"{current_month}월", "마감임박"]):
            return "urgent"

        return "normal"

    def _generate_tags(self, policy: Dict[str, Any]) -> List[str]:
        """정책 태그 생성"""
        tags = []

        # 카테고리 태그
        category = policy.get("category", "")
        if category:
            tags.append(category)

        # 기관 태그
        agency = self._extract_agency_from_policy(policy)
        if agency != "관련 기관":
            tags.append(agency)

        # 매칭 이유에서 태그 추출
        match_reasons = policy.get("match_reasons", [])
        for reason in match_reasons:
            if "나이" in reason:
                tags.append("연령적합")
            if "지역" in reason:
                tags.append("지역적합")
            if "소득" in reason:
                tags.append("소득적합")
            if "고용" in reason:
                employment_match = re.search(r'\(([^)]+)\)', reason)
                if employment_match:
                    employment_types = employment_match.group(1).split(', ')
                    tags.extend(employment_types)

        # 혜택 크기에 따른 태그
        score = policy.get("score", 0)
        if score >= 90:
            tags.append("고혜택")
        elif score >= 80:
            tags.append("우수혜택")

        # 중복 제거 및 최대 5개까지
        return list(dict.fromkeys(tags))[:5]

    def format_result(self, explained_policies: List[Dict[str, Any]],
                     user_profile: Dict[str, Any],
                     summary_stats: Optional[Dict[str, Any]] = None) -> FormattedResult:
        """
        매칭 결과를 UI 최적화된 형태로 포맷팅

        Args:
            explained_policies (List[Dict[str, Any]]): 설명이 포함된 정책 목록
            user_profile (Dict[str, Any]): 사용자 프로필
            summary_stats (Optional[Dict[str, Any]]): 요약 통계

        Returns:
            FormattedResult: 포맷된 결과
        """
        try:
            if not explained_policies:
                return FormattedResult(
                    success=False,
                    message="매칭되는 정책이 없습니다.",
                    user_profile_summary=self._create_profile_summary(user_profile),
                    total_count=0,
                    avg_score=0.0,
                    category_distribution={},
                    recommendations=[],
                    generated_at=datetime.now().isoformat()
                )

            # 정책 카드 생성
            policy_cards = []
            category_counts = {}
            total_score = 0.0

            for policy in explained_policies:
                # 카테고리별 카운트
                category = policy.get("category", "기타")
                category_counts[category] = category_counts.get(category, 0) + 1

                # 총 점수 누적
                score = policy.get("score", 0.0)
                total_score += score

                # 정책 카드 생성
                policy_card = PolicyCard(
                    policy_id=policy.get("policy_id", ""),
                    policy_name=policy.get("title", ""),
                    category=category,
                    agency=self._extract_agency_from_policy(policy),
                    score=score,
                    score_grade=self._get_score_grade(score),
                    benefit=policy.get("benefit_summary", ""),
                    explanation=policy.get("explanation", ""),
                    application_url=policy.get("application_url"),
                    deadline=policy.get("deadline"),
                    deadline_status=self._analyze_deadline_status(policy.get("deadline")),
                    tags=self._generate_tags(policy)
                )
                policy_cards.append(policy_card)

            # 평균 점수 계산
            avg_score = total_score / len(explained_policies) if explained_policies else 0.0

            # 비교 테이블 생성
            comparison_table = self.create_comparison_table(policy_cards)

            # 메시지 생성
            message = f"{len(explained_policies)}개의 맞춤 정책을 찾았습니다."
            if avg_score >= 85:
                message += " 매칭도가 매우 높습니다!"
            elif avg_score >= 75:
                message += " 좋은 조건의 정책들입니다."

            return FormattedResult(
                success=True,
                message=message,
                user_profile_summary=self._create_profile_summary(user_profile),
                total_count=len(explained_policies),
                avg_score=round(avg_score, 1),
                category_distribution=category_counts,
                recommendations=policy_cards,
                comparison_table=comparison_table,
                generated_at=datetime.now().isoformat()
            )

        except Exception as e:
            print(f"⚠️ Agent5: 결과 포맷팅 중 오류 - {e}")
            return FormattedResult(
                success=False,
                message=f"결과 포맷팅 중 오류가 발생했습니다: {str(e)}",
                user_profile_summary=self._create_profile_summary(user_profile),
                total_count=0,
                avg_score=0.0,
                category_distribution={},
                recommendations=[],
                generated_at=datetime.now().isoformat()
            )

    def create_comparison_table(self, policy_cards: List[PolicyCard]) -> ComparisonTable:
        """
        정책 비교 테이블 생성

        Args:
            policy_cards (List[PolicyCard]): 정책 카드 목록

        Returns:
            ComparisonTable: 비교 테이블
        """
        try:
            headers = ["정책명", "점수", "혜택", "주관기관", "마감일"]
            rows = []

            for card in policy_cards:
                row = ComparisonTableRow(
                    policy_name=card.policy_name,
                    score=f"{card.score}점 ({card.score_grade})",
                    benefit=card.benefit[:50] + "..." if len(card.benefit) > 50 else card.benefit,
                    agency=card.agency,
                    deadline=card.deadline or "미정"
                )
                rows.append(row)

            return ComparisonTable(headers=headers, rows=rows)

        except Exception as e:
            print(f"⚠️ Agent5: 비교 테이블 생성 중 오류 - {e}")
            return ComparisonTable(headers=[], rows=[])

    def _create_profile_summary(self, user_profile: Dict[str, Any]) -> str:
        """사용자 프로필 요약 생성"""
        try:
            age = user_profile.get("age", "미상")
            region = user_profile.get("region", "미상")
            income = user_profile.get("income", 0)
            employment = user_profile.get("employment", "미상")
            interest = user_profile.get("interest", "")

            summary = f"{age}세, {region} 거주, 연소득 {income:,}만원, {employment}"
            if interest:
                summary += f", 관심분야: {interest}"

            return summary
        except:
            return "프로필 정보를 확인할 수 없습니다."

    def get_formatting_stats(self) -> Dict[str, Any]:
        """
        Agent5 포맷팅 통계 반환

        Returns:
            Dict[str, Any]: 포맷팅 통계 정보
        """
        return {
            "agent_name": self.agent_name,
            "version": self.agent_version,
            "score_grades": self.score_grades,
            "supported_formats": ["PolicyCard", "ComparisonTable", "FormattedResult"],
            "status": "active"
        }


# 테스트 코드
if __name__ == "__main__":
    print("🤖 Agent 5 (결과 포맷팅) 테스트 시작...")
    print("=" * 50)

    agent5 = Agent5()

    # 테스트용 설명된 정책 데이터
    test_explained_policies = [
        {
            "policy_id": "JOB_001",
            "title": "청년내일채움공제",
            "category": "일자리",
            "score": 93.5,
            "match_reasons": [
                "나이 조건 부합 (15-34세)",
                "지역 조건 부합 (전국)",
                "고용 상태 적합 (구직자)"
            ],
            "benefit_summary": "2년 만기시 300만원~1200만원 지급",
            "deadline": "연중 상시",
            "explanation": "25세 구직자인 회원님께 완벽히 맞는 정책입니다. 2년간 근무하시면 목돈 마련이 가능합니다!"
        },
        {
            "policy_id": "FIN_001",
            "title": "청년희망적금",
            "category": "금융",
            "score": 81.0,
            "match_reasons": ["나이 조건 부합", "소득 조건 부합"],
            "benefit_summary": "월 10만원 적립시 정부지원금 10만원",
            "deadline": "2024년 12월 31일",
            "explanation": "적금으로 목돈 마련과 함께 정부지원도 받을 수 있는 좋은 기회입니다."
        },
        {
            "policy_id": "HOU_001",
            "title": "청년 전세자금대출",
            "category": "주거",
            "score": 88.2,
            "match_reasons": ["나이 조건 부합", "지역 조건 부합"],
            "benefit_summary": "전세자금 최대 2억원 대출",
            "deadline": "연중 상시",
            "explanation": "내 집 마련의 첫걸음, 저리로 대출 받을 수 있습니다."
        }
    ]

    # 테스트용 사용자 프로필
    test_user_profile = {
        "age": 25,
        "region": "서울",
        "income": 3000,
        "employment": "구직자",
        "interest": "일자리"
    }

    print("\n📊 Agent5 상태:")
    stats = agent5.get_formatting_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")

    print("\n" + "=" * 30)
    print("📋 결과 포맷팅 테스트")
    print("=" * 30)

    # 결과 포맷팅 테스트
    formatted_result = agent5.format_result(test_explained_policies, test_user_profile)

    print(f"성공 여부: {formatted_result.success}")
    print(f"메시지: {formatted_result.message}")
    print(f"사용자 요약: {formatted_result.user_profile_summary}")
    print(f"총 정책 수: {formatted_result.total_count}")
    print(f"평균 점수: {formatted_result.avg_score}")
    print(f"카테고리 분포: {formatted_result.category_distribution}")

    print(f"\n📋 정책 카드 ({len(formatted_result.recommendations)}개):")
    for i, card in enumerate(formatted_result.recommendations, 1):
        print(f"{i}. {card.policy_name}")
        print(f"   점수: {card.score}점 ({card.score_grade}등급)")
        print(f"   기관: {card.agency}")
        print(f"   마감: {card.deadline} ({card.deadline_status})")
        print(f"   태그: {', '.join(card.tags)}")
        print(f"   설명: {card.explanation[:50]}...")

    print(f"\n📋 비교 테이블:")
    if formatted_result.comparison_table:
        table = formatted_result.comparison_table
        print(" | ".join(table.headers))
        print("-" * 80)
        for row in table.rows:
            print(f"{row.policy_name} | {row.score} | {row.benefit[:20]}... | {row.agency} | {row.deadline}")

    # 빈 결과 테스트
    print("\n" + "=" * 30)
    print("📋 빈 결과 포맷팅 테스트")
    print("=" * 30)

    empty_result = agent5.format_result([], test_user_profile)
    print(f"빈 결과 메시지: {empty_result.message}")
    print(f"성공 여부: {empty_result.success}")

    print("\n✅ Agent 5 테스트 완료!")