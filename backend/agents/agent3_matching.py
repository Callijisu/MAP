"""
Agent 3: 정책 매칭 및 점수 계산 에이전트
청년 정책 추천 시스템의 세 번째 에이전트로, 사용자 프로필과 정책의 매칭도를 분석하고 점수를 산출합니다.
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field


class MatchingResult(BaseModel):
    """
    매칭 결과 모델
    Agent3의 정책 매칭 결과를 담는 데이터 모델
    """
    policy_id: str = Field(..., description="정책 고유 ID")
    title: str = Field(..., description="정책명")
    category: str = Field(..., description="정책 분야")
    score: float = Field(..., ge=0.0, le=100.0, description="매칭 점수 (0-100)")
    match_reasons: List[str] = Field(default=[], description="매칭 이유")
    benefit_summary: str = Field("", description="혜택 요약")
    deadline: Optional[str] = Field(None, description="신청 마감일")

    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "JOB_001",
                "title": "청년내일채움공제",
                "category": "일자리",
                "score": 85.5,
                "match_reasons": [
                    "나이 조건 부합 (15-34세)",
                    "지역 조건 부합 (전국)",
                    "고용 상태 적합 (구직자)"
                ],
                "benefit_summary": "2년 만기시 300만원~1200만원 지급",
                "deadline": "연중 상시"
            }
        }


class Agent3:
    """
    Agent 3: 정책 매칭 및 점수 계산 에이전트

    주요 기능:
    - 사용자 프로필과 정책 간 조건 매칭 검증
    - 매칭 점수 계산 (0-100점)
    - 혜택 크기 및 신청 용이성 평가
    - 최적 정책 추천 순위 결정
    """

    def __init__(self):
        """Agent3 초기화"""
        self.agent_name = "Policy Matching Agent"
        self.agent_version = "1.0.0"

        # 점수 배점 설정
        self.score_weights = {
            "condition_match": 40,      # 조건 일치도: 40점
            "benefit_size": 30,         # 혜택 크기: 30점
            "ease_of_application": 30   # 신청 용이성: 30점
        }

        # 조건별 세부 배점
        self.condition_weights = {
            "age": 10,          # 나이: 10점
            "region": 10,       # 지역: 10점
            "income": 10,       # 소득: 10점
            "employment": 10    # 고용상태: 10점
        }

    def check_age_match(self, user_age: int, policy_age_min: int, policy_age_max: int) -> Tuple[bool, float]:
        """
        나이 조건 매칭 검사

        Args:
            user_age (int): 사용자 나이
            policy_age_min (int): 정책 최소 나이
            policy_age_max (int): 정책 최대 나이

        Returns:
            Tuple[bool, float]: (매칭 여부, 점수)
        """
        try:
            # 나이 범위 체크
            if policy_age_min <= user_age <= policy_age_max:
                # 나이가 정확히 가운데에 있을 때 만점, 경계에 가까울수록 점수 감소
                age_range = policy_age_max - policy_age_min
                if age_range == 0:
                    score = self.condition_weights["age"]
                else:
                    # 가운데에서 얼마나 떨어져 있는지 계산
                    center = (policy_age_min + policy_age_max) / 2
                    distance_from_center = abs(user_age - center)
                    max_distance = age_range / 2

                    # 거리에 따른 점수 계산 (가까울수록 높은 점수)
                    score_ratio = 1 - (distance_from_center / max_distance)
                    score = self.condition_weights["age"] * max(score_ratio, 0.5)  # 최소 50%는 보장

                return True, score
            else:
                return False, 0.0

        except Exception as e:
            print(f"⚠️ 나이 매칭 검사 오류: {e}")
            return False, 0.0

    def check_region_match(self, user_region: str, policy_regions: List[str]) -> Tuple[bool, float]:
        """
        지역 조건 매칭 검사

        Args:
            user_region (str): 사용자 거주 지역
            policy_regions (List[str]): 정책 대상 지역 목록

        Returns:
            Tuple[bool, float]: (매칭 여부, 점수)
        """
        try:
            # "전국"이 포함되어 있으면 무조건 매칭
            if "전국" in policy_regions:
                return True, self.condition_weights["region"]

            # 사용자 지역이 정책 대상 지역에 포함되는지 확인
            if user_region in policy_regions:
                # 대상 지역이 적을수록 더 높은 점수 (더 타겟팅된 정책)
                region_count = len(policy_regions)
                if region_count == 1:
                    score = self.condition_weights["region"]
                elif region_count <= 3:
                    score = self.condition_weights["region"] * 0.9
                elif region_count <= 5:
                    score = self.condition_weights["region"] * 0.8
                else:
                    score = self.condition_weights["region"] * 0.7

                return True, score
            else:
                return False, 0.0

        except Exception as e:
            print(f"⚠️ 지역 매칭 검사 오류: {e}")
            return False, 0.0

    def check_income_match(self, user_income: int, policy_income_max: Optional[int]) -> Tuple[bool, float]:
        """
        소득 조건 매칭 검사

        Args:
            user_income (int): 사용자 연 소득 (만원)
            policy_income_max (Optional[int]): 정책 최대 소득 제한 (만원)

        Returns:
            Tuple[bool, float]: (매칭 여부, 점수)
        """
        try:
            # 소득 제한이 없는 경우 (None 또는 0)
            if policy_income_max is None or policy_income_max == 0:
                return True, self.condition_weights["income"]

            # 사용자 소득이 정책 제한 내에 있는지 확인
            if user_income <= policy_income_max:
                # 여유분이 많을수록 높은 점수
                income_ratio = user_income / policy_income_max

                if income_ratio <= 0.5:
                    # 제한의 50% 이하 → 만점
                    score = self.condition_weights["income"]
                elif income_ratio <= 0.7:
                    # 제한의 70% 이하 → 90%
                    score = self.condition_weights["income"] * 0.9
                elif income_ratio <= 0.9:
                    # 제한의 90% 이하 → 80%
                    score = self.condition_weights["income"] * 0.8
                else:
                    # 제한에 가까움 → 70%
                    score = self.condition_weights["income"] * 0.7

                return True, score
            else:
                return False, 0.0

        except Exception as e:
            print(f"⚠️ 소득 매칭 검사 오류: {e}")
            return False, 0.0

    def check_employment_match(self, user_employment: str, policy_employment: List[str]) -> Tuple[bool, float]:
        """
        고용 상태 조건 매칭 검사

        Args:
            user_employment (str): 사용자 고용 상태
            policy_employment (List[str]): 정책 대상 고용 상태 목록

        Returns:
            Tuple[bool, float]: (매칭 여부, 점수)
        """
        try:
            # 고용 상태가 정책 대상에 포함되는지 확인
            if user_employment in policy_employment:
                # 대상 고용상태가 적을수록 더 높은 점수 (더 타겟팅된 정책)
                employment_count = len(policy_employment)
                if employment_count == 1:
                    score = self.condition_weights["employment"]
                elif employment_count <= 2:
                    score = self.condition_weights["employment"] * 0.9
                elif employment_count <= 3:
                    score = self.condition_weights["employment"] * 0.8
                else:
                    score = self.condition_weights["employment"] * 0.7

                return True, score
            else:
                return False, 0.0

        except Exception as e:
            print(f"⚠️ 고용상태 매칭 검사 오류: {e}")
            return False, 0.0

    def calculate_benefit_score(self, benefit: str, budget_max: Optional[int] = None) -> float:
        """
        혜택 크기 점수 계산

        Args:
            benefit (str): 혜택 설명 문자열
            budget_max (Optional[int]): 최대 지원 금액 (만원)

        Returns:
            float: 혜택 점수 (0-30점)
        """
        try:
            max_score = self.score_weights["benefit_size"]

            # budget_max가 있으면 우선 사용
            if budget_max and budget_max > 0:
                amount = budget_max
            else:
                # benefit 문자열에서 금액 추출
                amount = self._extract_amount_from_text(benefit)

            if amount == 0:
                return max_score * 0.3  # 금액 정보 없으면 30%

            # 금액에 따른 점수 계산
            if amount >= 3000:      # 3000만원 이상
                return max_score
            elif amount >= 2000:    # 2000만원 이상
                return max_score * 0.9
            elif amount >= 1000:    # 1000만원 이상
                return max_score * 0.8
            elif amount >= 500:     # 500만원 이상
                return max_score * 0.7
            elif amount >= 200:     # 200만원 이상
                return max_score * 0.6
            elif amount >= 100:     # 100만원 이상
                return max_score * 0.5
            elif amount >= 50:      # 50만원 이상
                return max_score * 0.4
            else:
                return max_score * 0.3

        except Exception as e:
            print(f"⚠️ 혜택 점수 계산 오류: {e}")
            return self.score_weights["benefit_size"] * 0.3

    def _extract_amount_from_text(self, text: str) -> int:
        """
        텍스트에서 금액 추출

        Args:
            text (str): 금액이 포함된 텍스트

        Returns:
            int: 추출된 금액 (만원 단위)
        """
        try:
            # 다양한 금액 표현 패턴 매칭
            patterns = [
                r'(\d+,?\d*)\s*만원',           # "3000만원", "1,000만원"
                r'(\d+,?\d*)\s*억',             # "1억"
                r'최대\s*(\d+,?\d*)\s*만원',     # "최대 3000만원"
                r'월\s*(\d+,?\d*)\s*만원',       # "월 50만원"
                r'(\d+,?\d*)\s*천만원',          # "5천만원"
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # 쉼표 제거 후 숫자 변환
                    amount_str = matches[0].replace(',', '')
                    amount = int(amount_str)

                    # 단위에 따른 변환
                    if '억' in text:
                        amount = amount * 10000  # 억 → 만원
                    elif '천만원' in text:
                        amount = amount * 1000   # 천만원 → 만원
                    elif '월' in text:
                        amount = amount * 12     # 월 → 연간

                    return amount

            return 0

        except Exception as e:
            print(f"⚠️ 금액 추출 오류: {e}")
            return 0

    def calculate_ease_score(self, policy: Dict[str, Any]) -> float:
        """
        신청 용이성 점수 계산

        Args:
            policy (Dict[str, Any]): 정책 정보

        Returns:
            float: 신청 용이성 점수 (0-30점)
        """
        try:
            max_score = self.score_weights["ease_of_application"]
            total_score = 0.0

            # 1. 신청 URL 존재 여부 (10점)
            application_url = policy.get("application_url") or policy.get("website_url", "")
            if application_url and application_url != "":
                total_score += max_score / 3

            # 2. 마감일 여유도 (10점)
            deadline = policy.get("deadline", "")
            if deadline:
                if any(word in deadline for word in ["상시", "연중", "수시"]):
                    # 상시 접수 → 만점
                    total_score += max_score / 3
                elif self._is_deadline_far(deadline):
                    # 마감일이 6개월 이상 남음 → 80%
                    total_score += (max_score / 3) * 0.8
                elif self._is_deadline_soon(deadline):
                    # 마감일이 가까움 → 40%
                    total_score += (max_score / 3) * 0.4
                else:
                    # 기타 → 60%
                    total_score += (max_score / 3) * 0.6

            # 3. 신청 요건 복잡도 (10점)
            requirements = policy.get("requirements", [])
            if isinstance(requirements, list):
                req_count = len(requirements)
                if req_count <= 2:
                    # 요건 2개 이하 → 만점
                    total_score += max_score / 3
                elif req_count <= 4:
                    # 요건 4개 이하 → 80%
                    total_score += (max_score / 3) * 0.8
                elif req_count <= 6:
                    # 요건 6개 이하 → 60%
                    total_score += (max_score / 3) * 0.6
                else:
                    # 요건 많음 → 40%
                    total_score += (max_score / 3) * 0.4

            return min(total_score, max_score)

        except Exception as e:
            print(f"⚠️ 신청 용이성 점수 계산 오류: {e}")
            return self.score_weights["ease_of_application"] * 0.5

    def _is_deadline_far(self, deadline: str) -> bool:
        """마감일이 6개월 이상 남았는지 확인"""
        try:
            # 간단한 날짜 패턴 매칭
            if "2024" in deadline or "2025" in deadline:
                # 실제 프로젝트에서는 더 정교한 날짜 파싱 필요
                return True
            return False
        except:
            return False

    def _is_deadline_soon(self, deadline: str) -> bool:
        """마감일이 1개월 이내인지 확인"""
        try:
            # 간단한 판별 로직
            current_month = datetime.now().month
            if str(current_month) in deadline:
                return True
            return False
        except:
            return False

    def calculate_score(self, user_profile: Dict[str, Any], policy: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        사용자 프로필과 정책 간 총 매칭 점수 계산

        Args:
            user_profile (Dict[str, Any]): 사용자 프로필
            policy (Dict[str, Any]): 정책 정보

        Returns:
            Tuple[float, List[str]]: (총점, 매칭 이유 목록)
        """
        try:
            total_score = 0.0
            match_reasons = []

            # 1. 조건 일치도 점수 (40점)
            condition_score = 0.0

            # 나이 조건 체크
            age_match, age_score = self.check_age_match(
                user_profile.get("age", 0),
                policy.get("target_age_min", 0),
                policy.get("target_age_max", 100)
            )

            if age_match:
                condition_score += age_score
                match_reasons.append(
                    f"나이 조건 부합 ({policy.get('target_age_min')}-{policy.get('target_age_max')}세)"
                )
            else:
                return 0.0, ["나이 조건 불일치"]  # 나이가 안 맞으면 0점

            # 지역 조건 체크
            region_match, region_score = self.check_region_match(
                user_profile.get("region", ""),
                policy.get("target_regions", [])
            )

            if region_match:
                condition_score += region_score
                regions_str = ", ".join(policy.get("target_regions", []))
                match_reasons.append(f"지역 조건 부합 ({regions_str})")

            # 소득 조건 체크
            income_match, income_score = self.check_income_match(
                user_profile.get("income", 0),
                policy.get("target_income_max")
            )

            if income_match:
                condition_score += income_score
                if policy.get("target_income_max"):
                    match_reasons.append(f"소득 조건 부합 ({policy.get('target_income_max'):,}만원 이하)")
                else:
                    match_reasons.append("소득 제한 없음")

            # 고용상태 조건 체크
            employment_match, employment_score = self.check_employment_match(
                user_profile.get("employment", ""),
                policy.get("target_employment", [])
            )

            if employment_match:
                condition_score += employment_score
                employment_str = ", ".join(policy.get("target_employment", []))
                match_reasons.append(f"고용 상태 적합 ({employment_str})")

            total_score += condition_score

            # 2. 혜택 크기 점수 (30점)
            benefit_score = self.calculate_benefit_score(
                policy.get("benefit", ""),
                policy.get("budget_max")
            )
            total_score += benefit_score

            if benefit_score > 20:
                match_reasons.append("높은 지원 혜택")
            elif benefit_score > 10:
                match_reasons.append("적정 지원 혜택")

            # 3. 신청 용이성 점수 (30점)
            ease_score = self.calculate_ease_score(policy)
            total_score += ease_score

            if ease_score > 20:
                match_reasons.append("신청 절차 간편")
            elif ease_score > 15:
                match_reasons.append("신청 절차 보통")

            return round(total_score, 1), match_reasons

        except Exception as e:
            print(f"⚠️ 점수 계산 오류: {e}")
            return 0.0, [f"점수 계산 중 오류 발생: {str(e)}"]

    def match_policies(self, user_profile: Dict[str, Any], policies: List[Dict[str, Any]],
                      min_score: float = 40.0, max_results: int = 10) -> List[MatchingResult]:
        """
        사용자 프로필에 맞는 정책들을 매칭하고 점수순으로 정렬

        Args:
            user_profile (Dict[str, Any]): 사용자 프로필
            policies (List[Dict[str, Any]]): 정책 목록
            min_score (float): 최소 매칭 점수 (기본 40점)
            max_results (int): 최대 반환 개수 (기본 10개)

        Returns:
            List[MatchingResult]: 매칭된 정책 결과 목록 (점수 높은 순)
        """
        try:
            matching_results = []

            for policy in policies:
                # 각 정책에 대해 점수 계산
                score, match_reasons = self.calculate_score(user_profile, policy)

                # 최소 점수 이상인 경우만 포함
                if score >= min_score:
                    result = MatchingResult(
                        policy_id=policy.get("policy_id", ""),
                        title=policy.get("title", ""),
                        category=policy.get("category", ""),
                        score=score,
                        match_reasons=match_reasons,
                        benefit_summary=policy.get("benefit", ""),
                        deadline=policy.get("deadline")
                    )
                    matching_results.append(result)

            # 점수 높은 순으로 정렬
            matching_results.sort(key=lambda x: (-x.score, x.deadline or ""))

            # 최대 개수만큼 반환
            return matching_results[:max_results]

        except Exception as e:
            print(f"⚠️ 정책 매칭 오류: {e}")
            return []

    def get_matching_summary(self, user_profile: Dict[str, Any],
                           matching_results: List[MatchingResult]) -> Dict[str, Any]:
        """
        매칭 결과 요약 정보 생성

        Args:
            user_profile (Dict[str, Any]): 사용자 프로필
            matching_results (List[MatchingResult]): 매칭 결과

        Returns:
            Dict[str, Any]: 매칭 요약 정보
        """
        try:
            if not matching_results:
                return {
                    "success": False,
                    "message": "매칭되는 정책이 없습니다.",
                    "user_profile_summary": self._get_user_profile_summary(user_profile),
                    "total_matches": 0,
                    "avg_score": 0.0,
                    "recommendations": []
                }

            # 통계 계산
            scores = [result.score for result in matching_results]
            avg_score = sum(scores) / len(scores)

            # 카테고리별 분포
            category_counts = {}
            for result in matching_results:
                category = result.category
                category_counts[category] = category_counts.get(category, 0) + 1

            return {
                "success": True,
                "message": f"{len(matching_results)}개의 맞춤 정책을 찾았습니다.",
                "user_profile_summary": self._get_user_profile_summary(user_profile),
                "total_matches": len(matching_results),
                "avg_score": round(avg_score, 1),
                "category_distribution": category_counts,
                "recommendations": [result.model_dump() for result in matching_results]
            }

        except Exception as e:
            print(f"⚠️ 매칭 요약 생성 오류: {e}")
            return {
                "success": False,
                "message": f"매칭 요약 생성 중 오류: {str(e)}",
                "user_profile_summary": "",
                "total_matches": 0,
                "avg_score": 0.0,
                "recommendations": []
            }

    def _get_user_profile_summary(self, user_profile: Dict[str, Any]) -> str:
        """사용자 프로필 요약 문자열 생성"""
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
            return "프로필 정보 오류"


# 테스트 코드
if __name__ == "__main__":
    print("🤖 Agent 3 (정책 매칭) 테스트 시작...")
    print("=" * 50)

    agent3 = Agent3()

    # 샘플 정책 데이터
    sample_policies = [
        {
            "policy_id": "JOB_001",
            "title": "청년내일채움공제",
            "category": "일자리",
            "target_age_min": 15,
            "target_age_max": 34,
            "target_regions": ["전국"],
            "target_employment": ["구직자"],
            "target_income_max": 6000,
            "benefit": "2년 만기시 300만원~1200만원 지급",
            "budget_max": 1200,
            "deadline": "연중 상시",
            "application_url": "https://www.work.go.kr"
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
            "benefit": "월 10만원 적립시 정부지원금 10만원 추가 적립",
            "budget_max": 240,
            "deadline": "2024년 12월 31일",
            "application_url": "https://www.finlife.or.kr"
        },
        {
            "policy_id": "HOU_001",
            "title": "청년 전세자금대출",
            "category": "주거",
            "target_age_min": 19,
            "target_age_max": 34,
            "target_regions": ["전국"],
            "target_employment": ["재직자", "구직자"],
            "target_income_max": 6000,
            "benefit": "전세자금 최대 2억원 대출",
            "budget_max": 20000,
            "deadline": "연중 상시",
            "application_url": "https://www.hf.go.kr"
        }
    ]

    # 테스트 케이스 1: 25세, 서울, 3000만원, 구직자
    print("\n📋 테스트 1: 25세, 서울, 3000만원, 구직자")
    user_profile_1 = {
        "age": 25,
        "region": "서울",
        "income": 3000,
        "employment": "구직자",
        "interest": "일자리"
    }

    results_1 = agent3.match_policies(user_profile_1, sample_policies)
    summary_1 = agent3.get_matching_summary(user_profile_1, results_1)

    print(f"매칭 결과: {summary_1['total_matches']}개 정책")
    print(f"평균 점수: {summary_1['avg_score']}점")
    for i, result in enumerate(results_1[:3]):
        print(f"{i+1}. {result.title} - {result.score}점")
        print(f"   이유: {', '.join(result.match_reasons[:2])}")

    # 테스트 케이스 2: 35세, 부산, 5000만원, 재직자
    print("\n📋 테스트 2: 35세, 부산, 5000만원, 재직자")
    user_profile_2 = {
        "age": 35,
        "region": "부산",
        "income": 5000,
        "employment": "재직자",
        "interest": "주거"
    }

    results_2 = agent3.match_policies(user_profile_2, sample_policies)
    summary_2 = agent3.get_matching_summary(user_profile_2, results_2)

    print(f"매칭 결과: {summary_2['total_matches']}개 정책")
    print(f"평균 점수: {summary_2['avg_score']}점")
    for i, result in enumerate(results_2[:3]):
        print(f"{i+1}. {result.title} - {result.score}점")
        print(f"   이유: {', '.join(result.match_reasons[:2])}")

    # 테스트 케이스 3: 조건 분석
    print("\n📋 테스트 3: 조건별 점수 분석")
    policy = sample_policies[0]
    score, reasons = agent3.calculate_score(user_profile_1, policy)
    print(f"정책: {policy['title']}")
    print(f"총점: {score}점")
    print(f"매칭 이유: {reasons}")

    print("\n✅ Agent 3 테스트 완료!")