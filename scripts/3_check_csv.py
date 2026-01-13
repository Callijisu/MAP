import csv
import os
from db_connect import connect_db

def export_db_to_csv():
    """DB 데이터를 CSV로 내보내기"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(base_dir, "data", "policies_db_dump.csv")

    print(f"🚀 [3단계] DB 검증: {output_file}")

    db = connect_db()
    if db is None:
        return

    policies = list(db.policies.find({}, {"_id": 0}))

    if not policies:
        print("❌ DB 비어있음!")
        return

    print(f"   🔍 {len(policies)}개 데이터 발견")

    all_headers = set()
    for p in policies:
        all_headers.update(p.keys())

    headers = ['policy_id', 'name', 'category', 'end_date'] + sorted([h for h in all_headers if h not in ['policy_id', 'name', 'category', 'end_date']])

    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(policies)

    print(f"🎉 검증 파일 생성 완료!")

if __name__ == "__main__":
    export_db_to_csv()