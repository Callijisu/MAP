import requests
import csv
import time
import os
import urllib3

# SSL 경고 메시지 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 🔑 API 키 입력 (본인 키로 교체하세요!)
# ==========================================
API_KEY = "여기에_발급받은_API_키를_넣으세요" 

# ✅ 최신 API 주소 (2026년 기준)
API_URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"

def fetch_and_save_raw_data():
    print(f"🚀 [1단계] 온통청년 API 데이터 수집 시작...")
    
    # 저장 경로 설정 (scripts 폴더의 상위 폴더인 data 폴더에 저장)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "data")
    output_file = os.path.join(output_dir, "policies_raw.csv")

    # data 폴더가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_policies = []
    page_num = 1
    page_size = 100 
    
    while True:
        try:
            # 최신 파라미터 적용 (apiKeyNm, pageNum, pageSize)
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
            
            # 데이터 추출 (root -> result -> youthPolicyList)
            result = data.get('result', {})
            current_policies = result.get('youthPolicyList', [])
            
            if not current_policies:
                print(f"✅ 수집 완료! (총 {len(all_policies)}개 수집됨)")
                break
                
            all_policies.extend(current_policies)
            print(f"   Build {page_num}페이지 수집 중... (+{len(current_policies)}개 / 누적 {len(all_policies)}개)")
            
            page_num += 1
            time.sleep(0.1) 
            
        except Exception as e:
            print(f"❌ 처리 중 에러 발생: {e}")
            break
            
    # CSV 저장
    if all_policies:
        headers = set()
        for p in all_policies:
            headers.update(p.keys())
        headers = sorted(list(headers))
        
        try:
            with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_policies)
                
            print(f"\n🎉 [성공] 원본 파일 생성 완료!")
            print(f"   위치: {output_file}")
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
    else:
        print("⚠️ 수집된 데이터가 0개입니다. API 키를 확인해주세요.")

if __name__ == "__main__":
    if "여기에" in API_KEY:
        print("🚨 API 키를 입력해주세요!")
    else:
        fetch_and_save_raw_data()