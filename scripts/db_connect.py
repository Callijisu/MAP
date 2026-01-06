import os
from pymongo import MongoClient
from dotenv import load_dotenv

# .env 파일 내용을 불러옵니다.
load_dotenv()

def connect_db():
    # .env에서 주소 가져오기
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        print("경고: .env 파일에서 MONGO_URI를 찾을 수 없습니다.")
        return

    try:
        # 1. 클라이언트 생성 (접속 시도)
        client = MongoClient(mongo_uri)
        
        # 2. 서버 정보 확인 (연결 테스트)
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공! (Ping 테스트 통과)")
        
        # 3. 데이터베이스 선택 (없으면 자동으로 만들어짐)
        db = client.youth_policy_db
        return db

    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")

if __name__ == "__main__":
    connect_db()