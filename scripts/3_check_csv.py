import csv
import os
from db_connect import connect_db

def export_db_to_csv():
    # 저장 경로 설정 (data/policies_db_dump.csv)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(base_dir, "data", "policies_db_dump.csv")
    
    print(f"🚀 [3단계] DB 데이터 검증 (결과물: {output_file})")
    
    db = connect_db()
    if db is None: return

    # DB에서 모든 정책 가져오기
    policies = list(db.policies.find({}, {"_id": 0}))
    
    if not policies:
        print("❌ DB가 비어있습니다! (2단계 코드를 실행했나요?)")
        return

    print(f"   🔍 총 {len(policies)}개의 데이터를 찾았습니다.")

    # 모든 헤더 자동 수집
    all_headers = set()
    for p in policies:
        all_headers.update(p.keys())
    
    # 보기 좋게 정렬 (policy_id, name을 앞으로)
    priority_headers = ['policy_id', 'name', 'category', 'end_date']
    other_headers = sorted([h for h in all_headers if h not in priority_headers])
    headers = priority_headers + other_headers

    try:
        with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(policies)
                
        print(f"🎉 [성공] 검증용 파일 생성 완료!")
        print(f"   이제 이 파일을 열어서 데이터가 잘 들어갔는지 확인해보세요.")

    except Exception as e:
        print(f"❌ 저장 실패: {e}")

if __name__ == "__main__":
    export_db_to_csv()