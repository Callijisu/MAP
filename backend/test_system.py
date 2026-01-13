#!/usr/bin/env python3
"""
청년 정책 추천 시스템 - 종합 시스템 테스트
Stage 10: 최종 점검을 위한 자동화 테스트 스크립트
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# 테스트 설정
BASE_URL = "http://localhost:8001"
TEST_TIMEOUT = 30


class SystemTester:
    """시스템 종합 테스트 클래스"""

    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": [],
            "performance_stats": {},
            "test_details": []
        }
        self.start_time = None

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 청년 정책 추천 시스템 - 종합 테스트 시작")
        print("=" * 60)

        self.start_time = time.time()

        try:
            # 1. 서버 기본 상태 확인
            self.test_server_health()

            # 2. 5가지 다른 사용자 프로필 테스트
            self.test_user_profiles()

            # 3. API 엔드포인트 테스트
            self.test_all_endpoints()

            # 4. 에러 처리 테스트
            self.test_error_handling()

            # 5. 성능 테스트
            self.test_performance()

            # 6. MongoDB 연결 테스트
            self.test_database_connectivity()

        except KeyboardInterrupt:
            print("\n⚠️ 테스트가 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ 테스트 실행 중 오류 발생: {e}")

        finally:
            self.print_final_report()

    def test_server_health(self):
        """서버 상태 및 기본 엔드포인트 테스트"""
        print("\n📡 1. 서버 상태 확인...")

        # Root endpoint
        self.assert_request("GET", "/", "시스템 정보 조회")

        # Health check
        self.assert_request("GET", "/health", "헬스 체크")

        print("✅ 서버 상태 확인 완료")

    def test_user_profiles(self):
        """5가지 다른 사용자 프로필로 전체 플로우 테스트"""
        print("\n👥 2. 다양한 사용자 프로필 테스트...")

        test_profiles = [
            {
                "name": "취업 준비생",
                "data": {
                    "age": 25,
                    "region": "서울",
                    "income": 0,
                    "employment": "구직자",
                    "interest": "일자리"
                }
            },
            {
                "name": "청년 창업가",
                "data": {
                    "age": 29,
                    "region": "부산",
                    "income": 2000,
                    "employment": "자영업",
                    "interest": "창업"
                }
            },
            {
                "name": "신입 사원",
                "data": {
                    "age": 24,
                    "region": "대전",
                    "income": 3500,
                    "employment": "재직자",
                    "interest": "주거"
                }
            },
            {
                "name": "프리랜서",
                "data": {
                    "age": 32,
                    "region": "대구",
                    "income": 4000,
                    "employment": "자영업",
                    "interest": "금융"
                }
            },
            {
                "name": "경력직 직장인",
                "data": {
                    "age": 35,
                    "region": "인천",
                    "income": 6000,
                    "employment": "재직자",
                    "interest": "교육"
                }
            }
        ]

        for i, profile in enumerate(test_profiles, 1):
            print(f"\n  📋 프로필 {i}: {profile['name']}")

            # 프로필 생성
            response = self.assert_request("POST", "/api/profile",
                                         f"프로필 생성 - {profile['name']}",
                                         json_data=profile['data'])

            if response:
                try:
                    profile_id = response.json().get('profile_id')
                    if profile_id:
                        # 통합 추천 테스트
                        orchestrator_data = profile['data'].copy()
                        orchestrator_data['min_score'] = 40.0
                        orchestrator_data['max_results'] = 5

                        self.assert_request("POST", "/api/orchestrator",
                                          f"통합 추천 - {profile['name']}",
                                          json_data=orchestrator_data)

                        # 정책 매칭 테스트
                        self.assert_request("POST", "/api/match",
                                          f"정책 매칭 - {profile['name']}",
                                          json_data=orchestrator_data)
                except Exception as e:
                    self.add_error(f"프로필 {profile['name']} 테스트 중 오류: {e}")

        print("✅ 사용자 프로필 테스트 완료")

    def test_all_endpoints(self):
        """모든 API 엔드포인트 체계적 테스트"""
        print("\n🔗 3. 전체 API 엔드포인트 테스트...")

        endpoints = [
            ("GET", "/", "시스템 정보"),
            ("GET", "/health", "헬스 체크"),
            ("GET", "/api/policies", "정책 목록 조회"),
            ("GET", "/api/policies?category=창업&page=1&limit=10", "정책 필터링"),
            ("GET", "/docs", "API 문서")
        ]

        for method, path, description in endpoints:
            self.assert_request(method, path, description)

        # POST 엔드포인트 테스트 (샘플 데이터)
        sample_profile = {
            "age": 27,
            "region": "서울",
            "income": 3000,
            "employment": "재직자",
            "interest": "창업"
        }

        self.assert_request("POST", "/api/profile", "프로필 생성 테스트", json_data=sample_profile)
        self.assert_request("POST", "/api/match", "정책 매칭 테스트", json_data=sample_profile)

        print("✅ API 엔드포인트 테스트 완료")

    def test_error_handling(self):
        """에러 처리 및 예외 상황 테스트"""
        print("\n⚠️ 4. 에러 처리 테스트...")

        # 잘못된 데이터로 프로필 생성
        invalid_profiles = [
            {"age": 17, "region": "서울", "income": 3000, "employment": "재직자"},  # 나이 제한
            {"age": 40, "region": "서울", "income": 3000, "employment": "재직자"},  # 나이 제한
            {"age": 25, "region": "", "income": 3000, "employment": "재직자"},     # 빈 지역
            {"age": 25, "region": "서울", "income": -1000, "employment": "재직자"}, # 음수 소득
        ]

        for i, invalid_data in enumerate(invalid_profiles, 1):
            response = requests.post(f"{BASE_URL}/api/profile",
                                   json=invalid_data,
                                   timeout=TEST_TIMEOUT)

            if response.status_code == 400:
                self.passed_test(f"잘못된 데이터 검증 {i} - 올바르게 거부됨")
            else:
                self.failed_test(f"잘못된 데이터 검증 {i} - 부적절한 응답 코드: {response.status_code}")

        # 존재하지 않는 엔드포인트
        response = requests.get(f"{BASE_URL}/api/nonexistent", timeout=TEST_TIMEOUT)
        if response.status_code == 404:
            self.passed_test("존재하지 않는 엔드포인트 - 올바르게 404 반환")
        else:
            self.failed_test(f"존재하지 않는 엔드포인트 - 예상과 다른 응답: {response.status_code}")

        print("✅ 에러 처리 테스트 완료")

    def test_performance(self):
        """성능 측정 테스트"""
        print("\n⚡ 5. 성능 측정...")

        # 추천 API 응답 시간 측정
        sample_profile = {
            "age": 28,
            "region": "서울",
            "income": 3500,
            "employment": "재직자",
            "interest": "창업",
            "min_score": 40.0,
            "max_results": 5
        }

        # Orchestrator 성능 측정
        start_time = time.time()
        response = self.assert_request("POST", "/api/orchestrator", "성능 측정 - 통합 추천", json_data=sample_profile)
        orchestrator_time = time.time() - start_time

        # 매칭 API 성능 측정
        start_time = time.time()
        response = self.assert_request("POST", "/api/match", "성능 측정 - 정책 매칭", json_data=sample_profile)
        matching_time = time.time() - start_time

        # 정책 조회 성능 측정
        start_time = time.time()
        response = self.assert_request("GET", "/api/policies", "성능 측정 - 정책 조회")
        policies_time = time.time() - start_time

        self.results["performance_stats"] = {
            "orchestrator_response_time": round(orchestrator_time, 3),
            "matching_response_time": round(matching_time, 3),
            "policies_response_time": round(policies_time, 3)
        }

        # 성능 기준 검증 (5초 목표)
        if orchestrator_time < 5.0:
            self.passed_test(f"Orchestrator 성능 목표 달성 ({orchestrator_time:.3f}s < 5.0s)")
        else:
            self.failed_test(f"Orchestrator 성능 목표 미달성 ({orchestrator_time:.3f}s >= 5.0s)")

        print("✅ 성능 측정 완료")

    def test_database_connectivity(self):
        """MongoDB 연결 안정성 테스트"""
        print("\n💾 6. 데이터베이스 연결 테스트...")

        # 헬스 체크를 통한 DB 상태 확인
        response = self.assert_request("GET", "/health", "데이터베이스 연결 상태")

        if response:
            try:
                health_data = response.json()
                if health_data.get("database") == "connected":
                    self.passed_test("MongoDB 연결 - 정상 연결됨")

                    # DB 정보 확인
                    db_info = health_data.get("database_info", {})
                    if db_info:
                        print(f"    📊 DB 이름: {db_info.get('name', 'N/A')}")
                        print(f"    📁 컬렉션 수: {db_info.get('collections', 'N/A')}")
                        print(f"    💿 DB 크기: {db_info.get('size_mb', 'N/A')} MB")
                else:
                    self.failed_test(f"MongoDB 연결 - 연결되지 않음: {health_data.get('database')}")
            except Exception as e:
                self.add_error(f"DB 상태 확인 중 오류: {e}")

        print("✅ 데이터베이스 연결 테스트 완료")

    def assert_request(self, method: str, path: str, description: str, json_data: Dict = None) -> Optional[requests.Response]:
        """HTTP 요청 실행 및 검증"""
        self.results["total_tests"] += 1

        try:
            url = f"{BASE_URL}{path}"

            if method == "GET":
                response = requests.get(url, timeout=TEST_TIMEOUT)
            elif method == "POST":
                response = requests.post(url, json=json_data, timeout=TEST_TIMEOUT)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메소드: {method}")

            if 200 <= response.status_code < 300:
                self.passed_test(description)
                return response
            else:
                self.failed_test(f"{description} - HTTP {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            self.failed_test(f"{description} - 타임아웃 ({TEST_TIMEOUT}초)")
            return None
        except requests.exceptions.ConnectionError:
            self.failed_test(f"{description} - 서버 연결 실패")
            return None
        except Exception as e:
            self.failed_test(f"{description} - 오류: {str(e)}")
            return None

    def passed_test(self, description: str):
        """테스트 통과"""
        self.results["passed_tests"] += 1
        self.results["test_details"].append({"status": "PASS", "description": description})
        print(f"    ✅ {description}")

    def failed_test(self, description: str):
        """테스트 실패"""
        self.results["failed_tests"] += 1
        self.results["test_details"].append({"status": "FAIL", "description": description})
        print(f"    ❌ {description}")

    def add_error(self, error_msg: str):
        """에러 추가"""
        self.results["errors"].append(error_msg)
        print(f"    ⚠️ {error_msg}")

    def print_final_report(self):
        """최종 테스트 결과 리포트 출력"""
        total_time = time.time() - self.start_time if self.start_time else 0

        print("\n" + "=" * 60)
        print("📊 === 최종 테스트 결과 리포트 ===")
        print(f"🕐 총 실행 시간: {total_time:.2f}초")
        print(f"📝 총 테스트 수: {self.results['total_tests']}")
        print(f"✅ 통과: {self.results['passed_tests']}")
        print(f"❌ 실패: {self.results['failed_tests']}")

        if self.results["performance_stats"]:
            print("\n⚡ 성능 통계:")
            for metric, value in self.results["performance_stats"].items():
                print(f"   {metric}: {value}초")

        if self.results["errors"]:
            print(f"\n⚠️ 오류 목록 ({len(self.results['errors'])}개):")
            for i, error in enumerate(self.results["errors"], 1):
                print(f"   {i}. {error}")

        # 성공률 계산
        success_rate = (self.results["passed_tests"] / self.results["total_tests"] * 100) if self.results["total_tests"] > 0 else 0
        print(f"\n🎯 성공률: {success_rate:.1f}%")

        if success_rate >= 90:
            print("🎉 훌륭합니다! 시스템이 안정적으로 작동하고 있습니다.")
        elif success_rate >= 70:
            print("👍 양호합니다. 일부 개선이 필요할 수 있습니다.")
        else:
            print("⚠️ 주의: 여러 문제가 발견되었습니다. 시스템 점검이 필요합니다.")

        # 체크리스트 출력
        self.print_checklist()

    def print_checklist(self):
        """배포 체크리스트 출력"""
        print("\n✅ === 배포 준비 체크리스트 ===")

        checklist_items = [
            ("서버 기본 기능", self.results["passed_tests"] > 0),
            ("API 엔드포인트", self.results["failed_tests"] < self.results["total_tests"] // 2),
            ("에러 처리", "에러 처리" in str(self.results["test_details"])),
            ("성능 목표 (5초 이내)",
             self.results["performance_stats"].get("orchestrator_response_time", 10) < 5.0),
            ("데이터베이스 연결", "MongoDB" in str(self.results["test_details"])),
        ]

        for item, status in checklist_items:
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {item}")

        print("\n📋 추가 확인 필요 항목:")
        print("   📄 README.md 문서 완성도")
        print("   📚 API.md 문서 정확성")
        print("   🔒 .env 파일 보안 설정")
        print("   🚫 .gitignore 완성도")
        print("   📦 불필요한 파일 정리")


def main():
    """메인 함수"""
    print("청년 정책 추천 시스템 - 종합 테스트 도구")
    print("서버가 http://localhost:8001에서 실행 중인지 확인하세요.\n")

    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ 서버 연결 확인됨\n")
    except:
        print("❌ 서버에 연결할 수 없습니다.")
        print("다음 명령어로 서버를 시작하세요:")
        print("cd backend && python -m uvicorn main:app --port 8001 --reload\n")
        sys.exit(1)

    # 테스트 실행
    tester = SystemTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()