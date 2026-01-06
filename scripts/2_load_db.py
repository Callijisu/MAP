import csv
import time
import random
import os
from datetime import datetime
from db_connect import connect_db

def run_universal_loader():
    # 파일 경로 찾기 (data/policies_raw.csv)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "data", "policies_raw.csv")
    
    print(f"🚀 [2단계] 데이터 적재 시작: {csv_file} -> MongoDB")
    
    db = connect_db()
    if db is None: return

    # 1. 기존 데이터 초기화 (중복 방지)
    delete_result = db.policies.delete_many({}) 
    print(f"🧹 기존 데이터 {delete_result.deleted_count}개를 삭제하고 시작합니다.\n")

    saved_count = 0
    
    try:
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # 2. 데이터 매핑 (API 변수명 -> 우리 DB 변수명)
                # API가 주는 이름이 어려워서 여기서 한 번 번역해줍니다.
                policy = {
                    "policy_id": row.get('bizId') or row.get('plcyNo') or f"TEMP_{int(time.time())}_{random.randint(100,999)}",
                    
                    "name": row.get('polyBizSjnm') or row.get('plcyNm') or row.get('name', '이름없음'),
                    "category": row.get('polyBizSecd') or '기타',
                    "provider": row.get('polyBizTy') or row.get('pvsnInstGroupCd', '기타'),
                    "region": row.get('plcyRgn') or "전국/지자체",
                    
                    # 날짜는 일단 문자열 그대로 저장 (나중에 백엔드가 처리)
                    "start_date": "-", 
                    "end_date": row.get('rqutPrdCn') or row.get('plcyExplnCn', '-'),
                    
                    "url": row.get('rqutUrla') or row.get('etct', ''),
                    "support_content": row.get('polyItcnCn') or row.get('plcyExplnCn', ''),
                    
                    "qualification": {
                        "age_info": row.get('ageInfo') or '',
                        "job_status": row.get('empmSttsCn') or '',
                        "education": row.get('accrRqisCn') or ''
                    },
                    
                    "data_source": "raw_csv_upload",
                    "uploaded_at": datetime.now()
                }

                db.policies.insert_one(policy)
                saved_count += 1

    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {csv_file}")
        print("   👉 [1단계] 코드를 먼저 실행해서 데이터를 수집해주세요.")
        return
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return

    print("-" * 50)
    print(f"🎉 [성공] 총 {saved_count}개의 정책을 DB에 저장했습니다!")
    print("-" * 50)

if __name__ == "__main__":
    run_universal_loader()