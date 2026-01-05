"""
샘플 정책 데이터베이스 시드 스크립트
sample_policies.json 데이터를 MongoDB에 저장하는 스크립트
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, 'backend'))

# 환경변수 로드
load_dotenv(os.path.join(project_root, '.env'))

from database.mongo_handler import MongoDBHandler

def load_sample_policies():
    """
    sample_policies.json 파일에서 정책 데이터 로드

    Returns:
        List[Dict]: 정책 데이터 리스트
    """
    sample_file_path = os.path.join(project_root, 'data', 'sample_policies.json')

    try:
        with open(sample_file_path, 'r', encoding='utf-8') as file:
            policies = json.load(file)
            print(f"✅ 샘플 정책 파일 로드 완료: {len(policies)}개")
            return policies
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {sample_file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return []

def convert_policy_format(policy):
    """
    sample_policies.json 형식을 PolicyDB 형식으로 변환

    Args:
        policy (Dict): 원본 정책 데이터

    Returns:
        Dict: PolicyDB 형식 정책 데이터
    """
    return {
        "policy_id": policy["policy_id"],
        "title": policy["title"],
        "description": policy["description"],
        "category": policy["category"],
        "target_age_min": policy["target_age_min"],
        "target_age_max": policy["target_age_max"],
        "target_regions": policy["target_regions"],
        "target_employment": policy["target_employment"],
        "budget_min": policy.get("budget_min", 0),
        "budget_max": policy.get("budget_max", 0),
        "application_period": {
            "start": "2024-01-01",
            "end": policy.get("deadline", "2024-12-31")
        },
        "requirements": policy["requirements"],
        "documents": policy["documents"],
        "contact": policy["contact"],
        "website_url": policy["application_url"],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_active": True
    }

def seed_policies_database():
    """
    정책 데이터를 MongoDB에 저장

    Returns:
        Dict: 저장 결과 통계
    """
    print("🌱 정책 데이터베이스 시드 시작...")
    print("=" * 50)

    # MongoDB 핸들러 초기화
    try:
        db_handler = MongoDBHandler()
        if not db_handler.is_connected:
            print("❌ MongoDB 연결 실패")
            return {
                "success": False,
                "error": "MongoDB 연결 실패",
                "total_policies": 0,
                "inserted_count": 0,
                "failed_count": 0
            }
    except Exception as e:
        print(f"❌ MongoDB 핸들러 초기화 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_policies": 0,
            "inserted_count": 0,
            "failed_count": 0
        }

    # 샘플 정책 데이터 로드
    sample_policies = load_sample_policies()
    if not sample_policies:
        print("❌ 로드할 정책 데이터가 없습니다")
        return {
            "success": False,
            "error": "정책 데이터 로드 실패",
            "total_policies": 0,
            "inserted_count": 0,
            "failed_count": 0
        }

    # 정책 데이터 형식 변환
    converted_policies = []
    for policy in sample_policies:
        try:
            converted_policy = convert_policy_format(policy)
            converted_policies.append(converted_policy)
            print(f"✅ 변환 완료: {policy['policy_id']} - {policy['title']}")
        except Exception as e:
            print(f"❌ 변환 실패: {policy.get('policy_id', 'Unknown')} - {e}")

    if not converted_policies:
        print("❌ 변환된 정책 데이터가 없습니다")
        return {
            "success": False,
            "error": "정책 데이터 변환 실패",
            "total_policies": len(sample_policies),
            "inserted_count": 0,
            "failed_count": len(sample_policies)
        }

    print(f"\n📊 변환 결과:")
    print(f"   총 정책 수: {len(sample_policies)}")
    print(f"   변환 성공: {len(converted_policies)}")
    print(f"   변환 실패: {len(sample_policies) - len(converted_policies)}")

    # MongoDB에 일괄 저장
    print(f"\n💾 MongoDB에 정책 데이터 저장 중...")
    try:
        result = db_handler.save_multiple_policies(converted_policies)

        if result.get("success"):
            print(f"✅ 정책 데이터 저장 완료!")
            print(f"   저장된 정책 수: {result.get('inserted_count', 0)}")
            print(f"   MongoDB ID 개수: {len(result.get('inserted_ids', []))}")

            # 카테고리별 통계
            category_stats = {}
            for policy in converted_policies:
                category = policy["category"]
                category_stats[category] = category_stats.get(category, 0) + 1

            print(f"\n📈 카테고리별 저장 통계:")
            for category, count in category_stats.items():
                print(f"   {category}: {count}개")

            return {
                "success": True,
                "total_policies": len(sample_policies),
                "inserted_count": result.get('inserted_count', 0),
                "failed_count": len(sample_policies) - result.get('inserted_count', 0),
                "category_stats": category_stats,
                "inserted_ids": result.get('inserted_ids', [])
            }
        else:
            print(f"❌ 정책 데이터 저장 실패: {result.get('error')}")
            return {
                "success": False,
                "error": result.get('error'),
                "total_policies": len(sample_policies),
                "inserted_count": 0,
                "failed_count": len(sample_policies)
            }

    except Exception as e:
        print(f"❌ 데이터 저장 중 오류 발생: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_policies": len(sample_policies),
            "inserted_count": 0,
            "failed_count": len(sample_policies)
        }
    finally:
        # MongoDB 연결 종료
        db_handler.close()

def verify_seeded_data():
    """
    저장된 데이터 검증

    Returns:
        Dict: 검증 결과
    """
    print("\n🔍 저장된 데이터 검증 중...")

    try:
        db_handler = MongoDBHandler()
        if not db_handler.is_connected:
            print("❌ MongoDB 연결 실패")
            return {"success": False, "error": "MongoDB 연결 실패"}

        # 전체 정책 조회
        result = db_handler.get_all_policies()

        if result.get("success"):
            policies = result.get("policies", [])
            print(f"✅ 데이터베이스 검증 완료")
            print(f"   총 저장된 정책 수: {len(policies)}")

            # 카테고리별 확인
            categories = {}
            for policy in policies:
                cat = policy.get("category", "Unknown")
                categories[cat] = categories.get(cat, 0) + 1

            print(f"\n📊 데이터베이스 카테고리별 통계:")
            for category, count in categories.items():
                print(f"   {category}: {count}개")

            return {
                "success": True,
                "total_count": len(policies),
                "categories": categories
            }
        else:
            print(f"❌ 데이터 조회 실패: {result.get('error')}")
            return {"success": False, "error": result.get('error')}

    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db_handler.close()

if __name__ == "__main__":
    print("🚀 청년 정책 추천 시스템 - 데이터베이스 시드 스크립트")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 1. 데이터베이스 시드 실행
    seed_result = seed_policies_database()

    # 2. 결과 출력
    print("\n" + "=" * 50)
    if seed_result["success"]:
        print("🎉 데이터베이스 시드 성공!")
        print(f"   총 처리된 정책: {seed_result['total_policies']}")
        print(f"   성공적으로 저장: {seed_result['inserted_count']}")
        print(f"   실패한 저장: {seed_result['failed_count']}")

        # 3. 데이터 검증
        verify_result = verify_seeded_data()
        if verify_result["success"]:
            print(f"\n✅ 최종 검증 완료: 총 {verify_result['total_count']}개 정책이 데이터베이스에 저장됨")

    else:
        print("❌ 데이터베이스 시드 실패!")
        print(f"   오류: {seed_result.get('error')}")

    print(f"\n⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)