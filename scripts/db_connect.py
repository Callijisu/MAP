import os
from pymongo import MongoClient
from dotenv import load_dotenv

# backend/.env 파일 로드
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, 'backend', '.env')
load_dotenv(env_path)

def connect_db():
    """MongoDB 연결 함수"""
    # MONGODB_URI로 변경 (MONGO_URI 아님!)
    mongo_uri = os.getenv("MONGODB_URI")

    if not mongo_uri:
        print("❌ .env 파일에서 MONGODB_URI를 찾을 수 없습니다.")
        return None

    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")

        db_name = os.getenv("DATABASE_NAME", "youth_policy")
        db = client[db_name]
        return db

    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None

if __name__ == "__main__":
    connect_db()