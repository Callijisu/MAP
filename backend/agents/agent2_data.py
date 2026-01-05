"""
Agent 2: 정책 데이터 수집 및 관리 에이전트
청년 정책 추천 시스템의 두 번째 에이전트로, 정책 데이터의 수집, 저장, 조회를 담당합니다.
"""

import os
import requests
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# MongoDB 핸들러 임포트
try:
    from database.mongo_handler import get_mongodb_handler
except ImportError:
    print("⚠️ MongoDB 핸들러를 임포트할 수 없습니다. 데이터베이스 기능이 비활성화됩니다.")
    get_mongodb_handler = None


class PolicyFilter(BaseModel):
    """
    정책 필터 조건 모델
    사용자의 프로필 정보를 기반으로 정책을 필터링할 때 사용
    """
    category: Optional[str] = Field(None, description="정책 분야")
    age: Optional[int] = Field(None, ge=15, le=39, description="나이")
    region: Optional[str] = Field(None, description="거주 지역")
    employment: Optional[str] = Field(None, description="고용 상태")
    income: Optional[int] = Field(None, ge=0, description="연 소득 (만원)")
    active_only: bool = Field(True, description="활성 정책만 조회")


class PolicySummary(BaseModel):
    """
    정책 요약 정보 모델
    API 응답에서 사용할 간단한 정책 정보
    """
    policy_id: str = Field(..., description="정책 고유 ID")
    title: str = Field(..., description="정책명")
    category: str = Field(..., description="정책 분야")
    agency: Optional[str] = Field(None, description="담당 기관")
    benefit: Optional[str] = Field(None, description="지원 내용")
    deadline: Optional[str] = Field(None, description="신청 기한")


class Agent2:
    """
    Agent 2: 정책 데이터 수집 및 관리 에이전트

    주요 기능:
    - MongoDB에서 정책 데이터 조회
    - 외부 API로부터 정책 데이터 수집 (온통청년 API 등)
    - 정책 데이터 파싱 및 정제
    - 사용자 조건에 맞는 정책 필터링
    """

    def __init__(self, use_database: bool = True, api_key: Optional[str] = None):
        """
        Agent2 초기화

        Args:
            use_database (bool): MongoDB 사용 여부
            api_key (Optional[str]): 외부 API 키 (온통청년 API 등)
        """
        self.agent_name = "Policy Data Collection Agent"
        self.agent_version = "1.0.0"
        self.use_database = use_database
        self.api_key = api_key or os.getenv("YOUTHCENTER_API_KEY")

        # MongoDB 핸들러 초기화
        self.db_handler = None
        if self.use_database and get_mongodb_handler:
            try:
                self.db_handler = get_mongodb_handler()
                if self.db_handler.is_connected:
                    print(f"✅ {self.agent_name}: MongoDB 연결 성공")
                else:
                    print(f"⚠️ {self.agent_name}: MongoDB 연결 실패, 로컬 모드로 실행")
                    self.db_handler = None
            except Exception as e:
                print(f"⚠️ {self.agent_name}: MongoDB 초기화 실패 - {e}")
                self.db_handler = None

    def get_policies_from_db(self, filter_conditions: Optional[PolicyFilter] = None) -> Dict[str, Any]:
        """
        MongoDB에서 정책 데이터 조회

        Args:
            filter_conditions (Optional[PolicyFilter]): 필터 조건

        Returns:
            Dict[str, Any]: 조회 결과
        """
        try:
            if not self.db_handler:
                return {
                    "success": False,
                    "error": "데이터베이스 연결이 없습니다.",
                    "policies": []
                }

            # 기본 조회 (필터 조건이 없는 경우)
            if not filter_conditions:
                result = self.db_handler.get_all_policies()
                if result.get("success"):
                    policies = result.get("policies", [])

                    # PolicySummary 형식으로 변환
                    summary_policies = []
                    for policy in policies:
                        summary_policies.append(self._convert_to_summary(policy))

                    return {
                        "success": True,
                        "policies": summary_policies,
                        "count": len(summary_policies),
                        "source": "database",
                        "message": f"총 {len(summary_policies)}개의 정책을 조회했습니다."
                    }
                else:
                    return result

            # 카테고리 필터링
            if filter_conditions.category:
                result = self.db_handler.get_policies_by_category(
                    filter_conditions.category,
                    filter_conditions.active_only
                )
                if result.get("success"):
                    policies = result.get("policies", [])

                    # 추가 필터링 (나이, 지역, 소득 등)
                    filtered_policies = self._apply_additional_filters(policies, filter_conditions)

                    # PolicySummary 형식으로 변환
                    summary_policies = []
                    for policy in filtered_policies:
                        summary_policies.append(self._convert_to_summary(policy))

                    return {
                        "success": True,
                        "policies": summary_policies,
                        "count": len(summary_policies),
                        "category": filter_conditions.category,
                        "source": "database",
                        "message": f"'{filter_conditions.category}' 카테고리에서 {len(summary_policies)}개의 정책을 조회했습니다."
                    }
                else:
                    return result

            # 전체 조회 후 필터링
            result = self.db_handler.get_all_policies()
            if result.get("success"):
                policies = result.get("policies", [])
                filtered_policies = self._apply_additional_filters(policies, filter_conditions)

                # PolicySummary 형식으로 변환
                summary_policies = []
                for policy in filtered_policies:
                    summary_policies.append(self._convert_to_summary(policy))

                return {
                    "success": True,
                    "policies": summary_policies,
                    "count": len(summary_policies),
                    "source": "database",
                    "message": f"필터 조건에 맞는 {len(summary_policies)}개의 정책을 조회했습니다."
                }
            else:
                return result

        except Exception as e:
            return {
                "success": False,
                "error": f"정책 조회 중 오류가 발생했습니다: {str(e)}",
                "policies": []
            }

    def collect_from_api(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        외부 API에서 정책 데이터 수집 (온통청년 API 등)

        Args:
            api_key (Optional[str]): API 키

        Returns:
            Dict[str, Any]: 수집 결과
        """
        # TODO: 온통청년 API 연동 구현 예정
        # 실제 API 엔드포인트와 연동시 아래 코드를 참고하여 구현

        """
        온통청년 API 연동 예제 (TODO):

        try:
            # API 키 설정
            api_key = api_key or self.api_key
            if not api_key:
                return {
                    "success": False,
                    "error": "API 키가 설정되지 않았습니다."
                }

            # API 호출
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            api_url = "https://api.youthcenter.go.kr/openapi/policies"
            response = requests.get(api_url, headers=headers, timeout=30)

            if response.status_code == 200:
                raw_data = response.json()

                # 데이터 파싱 및 정제
                policies = []
                for item in raw_data.get("items", []):
                    parsed_policy = self.parse_policy(item)
                    if parsed_policy:
                        policies.append(parsed_policy)

                return {
                    "success": True,
                    "policies": policies,
                    "count": len(policies),
                    "source": "api",
                    "message": f"API에서 {len(policies)}개의 정책을 수집했습니다."
                }
            else:
                return {
                    "success": False,
                    "error": f"API 호출 실패: {response.status_code}",
                    "policies": []
                }

        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"API 호출 중 오류: {str(e)}",
                "policies": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"정책 수집 중 오류가 발생했습니다: {str(e)}",
                "policies": []
            }
        """

        return {
            "success": False,
            "error": "온통청년 API 연동 기능은 추후 구현 예정입니다.",
            "policies": [],
            "message": "현재 데이터베이스 조회 기능을 사용하세요."
        }

    def parse_policy(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        외부 API에서 받은 원시 정책 데이터를 파싱하여 내부 형식으로 변환

        Args:
            raw_data (Dict[str, Any]): 외부 API에서 받은 원시 데이터

        Returns:
            Optional[Dict[str, Any]]: 파싱된 정책 데이터 (실패시 None)
        """
        try:
            # TODO: 실제 API 데이터 구조에 맞게 파싱 로직 구현
            """
            온통청년 API 데이터 파싱 예제 (TODO):

            parsed_policy = {
                "policy_id": raw_data.get("bizId", f"api_{uuid.uuid4().hex[:8]}"),
                "title": raw_data.get("polyBizSjnm", "제목 없음"),
                "description": raw_data.get("polyItcnCn", ""),
                "category": self._map_category(raw_data.get("polyRlmCd", "")),
                "target_age_min": self._parse_age(raw_data.get("ageInfo", ""), "min"),
                "target_age_max": self._parse_age(raw_data.get("ageInfo", ""), "max"),
                "target_regions": self._parse_regions(raw_data.get("rqutUrla", "")),
                "target_employment": self._parse_employment(raw_data.get("empmSttsCn", "")),
                "budget_min": 0,
                "budget_max": self._parse_budget(raw_data.get("sprtCn", "")),
                "application_period": {
                    "start": raw_data.get("rqutPrdCn", "").split("~")[0].strip() if "~" in raw_data.get("rqutPrdCn", "") else "2024-01-01",
                    "end": raw_data.get("rqutPrdCn", "").split("~")[1].strip() if "~" in raw_data.get("rqutPrdCn", "") else "2024-12-31"
                },
                "requirements": [raw_data.get("rqutProcCn", "")],
                "documents": [],
                "contact": {
                    "department": raw_data.get("cnsgNmor", ""),
                    "phone": raw_data.get("tintCherCn", ""),
                    "email": ""
                },
                "website_url": raw_data.get("rfrncUrla", ""),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True
            }

            return parsed_policy
            """

            # 현재는 더미 데이터 반환
            return {
                "policy_id": f"api_{uuid.uuid4().hex[:8]}",
                "title": "API에서 수집된 정책",
                "description": "온통청년 API 연동 후 실제 데이터로 대체 예정",
                "category": "일자리",
                "target_age_min": 18,
                "target_age_max": 34,
                "target_regions": ["전국"],
                "target_employment": ["구직자"],
                "budget_min": 0,
                "budget_max": 1000,
                "application_period": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                },
                "requirements": ["API 연동 후 실제 요건 업데이트"],
                "documents": [],
                "contact": {
                    "department": "온통청년",
                    "phone": "1350",
                    "email": "api@youthcenter.go.kr"
                },
                "website_url": "https://youthcenter.go.kr",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True
            }

        except Exception as e:
            print(f"⚠️ 정책 데이터 파싱 실패: {e}")
            return None

    def _convert_to_summary(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """
        정책 데이터를 PolicySummary 형식으로 변환

        Args:
            policy (Dict[str, Any]): 원본 정책 데이터

        Returns:
            Dict[str, Any]: PolicySummary 형식 데이터
        """
        return {
            "policy_id": policy.get("policy_id", ""),
            "title": policy.get("title", ""),
            "category": policy.get("category", ""),
            "agency": policy.get("contact", {}).get("department", ""),
            "benefit": f"최대 {policy.get('budget_max', 0):,}만원 지원" if policy.get('budget_max') else "",
            "deadline": policy.get("application_period", {}).get("end", "")
        }

    def _apply_additional_filters(self, policies: List[Dict[str, Any]],
                                filter_conditions: PolicyFilter) -> List[Dict[str, Any]]:
        """
        추가 필터 조건 적용

        Args:
            policies (List[Dict[str, Any]]): 정책 리스트
            filter_conditions (PolicyFilter): 필터 조건

        Returns:
            List[Dict[str, Any]]: 필터링된 정책 리스트
        """
        filtered_policies = []

        for policy in policies:
            # 나이 조건 확인
            if filter_conditions.age is not None:
                age_min = policy.get("target_age_min", 0)
                age_max = policy.get("target_age_max", 100)
                if not (age_min <= filter_conditions.age <= age_max):
                    continue

            # 지역 조건 확인
            if filter_conditions.region:
                target_regions = policy.get("target_regions", [])
                if (filter_conditions.region not in target_regions and
                    "전국" not in target_regions):
                    continue

            # 고용 상태 조건 확인
            if filter_conditions.employment:
                target_employment = policy.get("target_employment", [])
                if filter_conditions.employment not in target_employment:
                    continue

            # 소득 조건 확인 (추후 확장 가능)
            if filter_conditions.income is not None:
                # TODO: 소득 조건 필터링 로직 추가
                pass

            filtered_policies.append(policy)

        return filtered_policies

    def get_policy_categories(self) -> Dict[str, Any]:
        """
        사용 가능한 정책 카테고리 목록 반환

        Returns:
            Dict[str, Any]: 카테고리 정보
        """
        categories = [
            {"code": "일자리", "name": "일자리", "description": "취업, 고용, 직업훈련 관련 정책"},
            {"code": "금융", "name": "금융", "description": "대출, 적금, 자산형성 관련 정책"},
            {"code": "주거", "name": "주거", "description": "전세, 월세, 주택구입 관련 정책"},
            {"code": "창업", "name": "창업", "description": "창업지원금, 사업자금 관련 정책"},
            {"code": "복지", "name": "복지", "description": "수당, 기본소득, 생활지원 관련 정책"},
            {"code": "교육", "name": "교육", "description": "학자금, 교육비, 훈련비 관련 정책"}
        ]

        return {
            "success": True,
            "categories": categories,
            "count": len(categories),
            "message": f"총 {len(categories)}개의 정책 카테고리가 있습니다."
        }

    def get_database_status(self) -> Dict[str, Any]:
        """
        데이터베이스 연결 상태 및 정책 통계 확인

        Returns:
            Dict[str, Any]: 데이터베이스 상태 정보
        """
        if not self.db_handler:
            return {
                "connected": False,
                "message": "MongoDB 핸들러가 초기화되지 않았습니다."
            }

        try:
            # 연결 상태 확인
            connection_status = self.db_handler.test_connection()

            if connection_status.get("connected"):
                # 정책 통계 조회
                policies_result = self.db_handler.get_all_policies()

                if policies_result.get("success"):
                    policies = policies_result.get("policies", [])

                    # 카테고리별 통계
                    category_stats = {}
                    for policy in policies:
                        category = policy.get("category", "기타")
                        category_stats[category] = category_stats.get(category, 0) + 1

                    return {
                        "connected": True,
                        "database_name": connection_status.get("database_name"),
                        "total_policies": len(policies),
                        "category_stats": category_stats,
                        "last_updated": datetime.now().isoformat()
                    }
                else:
                    return {
                        "connected": True,
                        "database_name": connection_status.get("database_name"),
                        "error": "정책 데이터 조회 실패"
                    }
            else:
                return connection_status

        except Exception as e:
            return {
                "connected": False,
                "error": f"상태 확인 중 오류: {str(e)}"
            }


# 테스트 코드
if __name__ == "__main__":
    print("🤖 Agent 2 (정책 데이터 수집) 테스트 시작...")
    print("=" * 50)

    agent2 = Agent2()

    # 테스트 케이스 1: 전체 정책 조회
    print("\n📋 테스트 1: 전체 정책 조회")
    result1 = agent2.get_policies_from_db()
    print(f"결과: {result1['success']}")
    if result1['success']:
        print(f"조회된 정책 수: {result1['count']}")
    else:
        print(f"오류: {result1['error']}")

    # 테스트 케이스 2: 카테고리별 조회
    print("\n📋 테스트 2: 카테고리별 정책 조회 (일자리)")
    filter_conditions = PolicyFilter(category="일자리")
    result2 = agent2.get_policies_from_db(filter_conditions)
    print(f"결과: {result2['success']}")
    if result2['success']:
        print(f"조회된 정책 수: {result2['count']}")

    # 테스트 케이스 3: 정책 카테고리 목록
    print("\n📋 테스트 3: 정책 카테고리 목록")
    categories_result = agent2.get_policy_categories()
    print(f"카테고리 수: {categories_result['count']}")

    # 테스트 케이스 4: 데이터베이스 상태
    print("\n📋 테스트 4: 데이터베이스 상태 확인")
    status_result = agent2.get_database_status()
    print(f"연결 상태: {status_result.get('connected', False)}")

    print("\n✅ Agent 2 테스트 완료!")