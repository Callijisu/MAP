import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, 'backend'))

# backend/.env 경로로 수정!
load_dotenv(os.path.join(project_root, 'backend', '.env'))

from database.mongo_handler import MongoDBHandler

def load_sample_policies():
    """sample_policies.json 로드"""
    sample_file_path = os.path.join(project_root, 'data', 'sample_policies.json')

    try:
        with open(sample_file_path, 'r', encoding='utf-8') as file:
            policies = json.load(file)
            print(f"✅ 샘플 정책 파일 로드: {len(policies)}개")
            return policies
    except FileNotFoundError:
        print(f"❌ 파일 없음: {sample_file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON 오류: {e}")
        return []

def convert_policy_format(policy):
    """PolicyDB 형식으로 변환"""
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
    """MongoDB에 정책 저장"""
    print("🌱 정책 데이터베이스 시드 시작...")

    try:
        db_handler = MongoDBHandler()
        if not db_handler.is_connected:
            print("❌ MongoDB 연결 실패")
            return {"success": False, "error": "연결 실패"}
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        return {"success": False, "error": str(e)}

    sample_policies = load_sample_policies()
    if not sample_policies:
        return {"success": False, "error": "데이터 없음"}

    converted_policies = []
    for policy in sample_policies:
        try:
            converted_policy = convert_policy_format(policy)
            converted_policies.append(converted_policy)
            print(f"✅ 변환: {policy['policy_id']}")
        except Exception as e:
            print(f"❌ 변환 실패: {e}")

    if not converted_policies:
        return {"success": False, "error": "변환 실패"}

    print(f"\n💾 MongoDB 저장 중...")
    try:
        result = db_handler.save_multiple_policies(converted_policies)

        if result.get("success"):
            print(f"✅ 저장 완료: {result.get('inserted_count')}개")
            return result
        else:
            print(f"❌ 저장 실패: {result.get('error')}")
            return result

    except Exception as e:
        print(f"❌ 저장 오류: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db_handler.close()

if __name__ == "__main__":
    print("🚀 데이터베이스 시드")
    result = seed_policies_database()

    if result["success"]:
        print("🎉 시드 완료!")
    else:
        print("❌ 시드 실패!")