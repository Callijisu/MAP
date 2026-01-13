import csv
import time
import random
import os
from datetime import datetime
from db_connect import connect_db

def run_universal_loader():
    """CSV 파일을 MongoDB에 로드"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "data", "policies_raw.csv")

    print(f"🚀 [2단계] 데이터 적재: {csv_file} -> MongoDB")

    db = connect_db()
    if db is None:
        return

    delete_result = db.policies.delete_many({})
    print(f"🧹 기존 데이터 {delete_result.deleted_count}개 삭제\n")

    saved_count = 0

    try:
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                policy = {
                    "policy_id": row.get('bizId') or f"TEMP_{int(time.time())}_{random.randint(100,999)}",
                    "name": row.get('polyBizSjnm') or "이름없음",
                    "category": row.get('polyBizSecd') or '기타',
                    "provider": row.get('polyBizTy') or '기타',
                    "region": row.get('plcyRgn') or "전국",
                    "end_date": row.get('rqutPrdCn') or '-',
                    "url": row.get('rqutUrla') or '',
                    "support_content": row.get('polyItcnCn') or '',
                    "qualification": {
                        "age_info": row.get('ageInfo') or '',
                        "job_status": row.get('empmSttsCn') or '',
                        "education": row.get('accrRqisCn') or ''
                    },
                    "uploaded_at": datetime.now()
                }

                db.policies.insert_one(policy)
                saved_count += 1

        print(f"🎉 총 {saved_count}개 정책 저장 완료!")

    except FileNotFoundError:
        print(f"❌ 파일 없음: {csv_file}")
        print("   1단계를 먼저 실행하세요.")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    run_universal_loader()