import requests
import csv
import time
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "여기에_발급받은_API_키를_넣으세요"
API_URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"

def fetch_and_save_raw_data():
    """온통청년 API에서 정책 데이터 수집"""
    print("🚀 [1단계] 온통청년 API 데이터 수집 시작...")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "data")
    output_file = os.path.join(output_dir, "policies_raw.csv")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_policies = []
    page_num = 1
    page_size = 100

    while True:
        try:
            params = {
                'apiKeyNm': API_KEY,
                'pageNum': page_num,
                'pageSize': page_size,
            }

            response = requests.get(API_URL, params=params, verify=False, timeout=10)

            if response.status_code != 200:
                print(f"❌ 요청 실패 (Code: {response.status_code})")
                break

            data = response.json()
            result = data.get('result', {})
            current_policies = result.get('youthPolicyList', [])

            if not current_policies:
                print(f"✅ 수집 완료! (총 {len(all_policies)}개)")
                break

            all_policies.extend(current_policies)
            print(f"   {page_num}페이지 수집 중... (+{len(current_policies)}개)")

            page_num += 1
            time.sleep(0.1)

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            break

    if all_policies:
        headers = set()
        for p in all_policies:
            headers.update(p.keys())
        headers = sorted(list(headers))

        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_policies)

        print(f"🎉 파일 생성 완료: {output_file}")
    else:
        print("⚠️ 데이터 0개. API 키를 확인하세요.")

if __name__ == "__main__":
    if "여기에" in API_KEY:
        print("🚨 API 키를 입력해주세요!")
    else:
        fetch_and_save_raw_data()