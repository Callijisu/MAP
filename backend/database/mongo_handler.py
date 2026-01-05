"""
MongoDB 데이터베이스 핸들러
청년 정책 추천 시스템의 MongoDB 연결 및 데이터 조작을 담당
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, DuplicateKeyError
from bson import ObjectId

from .models import UserProfileDB, PolicyDB, RecommendationDB, UserSessionDB


class MongoDBHandler:
    """
    MongoDB 데이터베이스 핸들러 클래스

    주요 기능:
    - MongoDB 연결 및 관리
    - 사용자 프로필 CRUD 작업
    - 정책 데이터 관리
    - 추천 이력 저장 및 조회
    - 세션 관리
    """

    def __init__(self, mongodb_uri: Optional[str] = None, database_name: Optional[str] = None):
        """
        MongoDBHandler 초기화

        Args:
            mongodb_uri (str, optional): MongoDB 연결 URI. None이면 환경변수에서 로드
            database_name (str, optional): 데이터베이스 이름. None이면 환경변수에서 로드
        """
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI")
        self.database_name = database_name or os.getenv("DATABASE_NAME", "youth_policy")

        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.is_connected = False

        # 컬렉션 이름 정의
        self.collections = {
            "user_profiles": "user_profiles",
            "policies": "policies",
            "recommendations": "recommendations",
            "user_sessions": "user_sessions"
        }

        # MongoDB 연결 시도
        self._connect()

    def _connect(self) -> None:
        """MongoDB 연결 수행"""
        try:
            if not self.mongodb_uri:
                raise ValueError("MongoDB URI가 설정되지 않았습니다. 환경변수 MONGODB_URI를 확인하세요.")

            # MongoDB 클라이언트 생성 (연결 타임아웃 설정)
            self.client = MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5초 타임아웃
                connectTimeoutMS=10000,         # 10초 연결 타임아웃
                socketTimeoutMS=20000,          # 20초 소켓 타임아웃
                maxPoolSize=10                  # 최대 연결 풀 크기
            )

            # 데이터베이스 선택
            self.database = self.client[self.database_name]

            # 연결 테스트
            self.client.admin.command('ismaster')
            self.is_connected = True

            print(f"✅ MongoDB 연결 성공: {self.database_name}")

            # 컬렉션 인덱스 생성
            self._create_indexes()

        except ConnectionFailure as e:
            print(f"❌ MongoDB 연결 실패: {e}")
            self.is_connected = False
        except ServerSelectionTimeoutError as e:
            print(f"❌ MongoDB 서버 선택 타임아웃: {e}")
            self.is_connected = False
        except Exception as e:
            print(f"❌ MongoDB 연결 중 예외 발생: {e}")
            self.is_connected = False

    def _create_indexes(self) -> None:
        """필요한 인덱스 생성"""
        try:
            # 사용자 프로필 인덱스
            profiles_collection = self.get_collection("user_profiles")
            profiles_collection.create_index("profile_id", unique=True)
            profiles_collection.create_index("created_at")

            # 정책 인덱스
            policies_collection = self.get_collection("policies")
            policies_collection.create_index("policy_id", unique=True)
            policies_collection.create_index("category")
            policies_collection.create_index([("target_age_min", 1), ("target_age_max", 1)])

            # 추천 인덱스
            recommendations_collection = self.get_collection("recommendations")
            recommendations_collection.create_index("user_profile_id")
            recommendations_collection.create_index("created_at")
            recommendations_collection.create_index("recommendation_id", unique=True)

            # 세션 인덱스
            sessions_collection = self.get_collection("user_sessions")
            sessions_collection.create_index("session_id", unique=True)
            sessions_collection.create_index("user_profile_id")
            sessions_collection.create_index("expires_at")

        except Exception as e:
            print(f"⚠️ 인덱스 생성 중 오류: {e}")

    def test_connection(self) -> Dict[str, Any]:
        """
        MongoDB 연결 상태 테스트

        Returns:
            Dict[str, Any]: 연결 상태 정보
        """
        try:
            if not self.client or not self.is_connected:
                return {
                    "connected": False,
                    "error": "MongoDB 클라이언트가 초기화되지 않았습니다."
                }

            # 서버 정보 조회
            server_info = self.client.admin.command('ismaster')
            db_stats = self.database.command('dbStats')

            return {
                "connected": True,
                "database_name": self.database_name,
                "server_version": server_info.get("version", "Unknown"),
                "collections_count": len(self.database.list_collection_names()),
                "database_size_mb": round(db_stats.get("dataSize", 0) / (1024 * 1024), 2),
                "test_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "test_time": datetime.now().isoformat()
            }

    def get_collection(self, collection_name: str) -> Collection:
        """
        컬렉션 반환

        Args:
            collection_name (str): 컬렉션 이름

        Returns:
            Collection: MongoDB 컬렉션 객체

        Raises:
            RuntimeError: 데이터베이스에 연결되지 않은 경우
        """
        if not self.is_connected or not self.database:
            raise RuntimeError("MongoDB에 연결되지 않았습니다.")

        return self.database[self.collections.get(collection_name, collection_name)]

    # === 사용자 프로필 관련 메서드 ===

    def save_user_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 프로필 저장

        Args:
            profile_data (Dict[str, Any]): 저장할 프로필 데이터

        Returns:
            Dict[str, Any]: 저장 결과
        """
        try:
            collection = self.get_collection("user_profiles")

            # UserProfileDB 모델로 검증
            profile = UserProfileDB(**profile_data)

            # MongoDB에 저장
            result = collection.insert_one(profile.model_dump(by_alias=True))

            return {
                "success": True,
                "profile_id": profile.profile_id,
                "mongodb_id": str(result.inserted_id),
                "message": "사용자 프로필이 성공적으로 저장되었습니다."
            }

        except DuplicateKeyError:
            return {
                "success": False,
                "error": f"이미 존재하는 프로필 ID입니다: {profile_data.get('profile_id')}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"프로필 저장 중 오류가 발생했습니다: {str(e)}"
            }

    def get_user_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        사용자 프로필 조회

        Args:
            profile_id (str): 조회할 프로필 ID

        Returns:
            Dict[str, Any]: 조회 결과
        """
        try:
            collection = self.get_collection("user_profiles")

            profile_doc = collection.find_one(
                {"profile_id": profile_id, "is_active": True}
            )

            if not profile_doc:
                return {
                    "success": False,
                    "error": f"프로필을 찾을 수 없습니다: {profile_id}"
                }

            # ObjectId를 문자열로 변환
            profile_doc["_id"] = str(profile_doc["_id"])

            return {
                "success": True,
                "profile": profile_doc,
                "message": "프로필 조회 완료"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"프로필 조회 중 오류가 발생했습니다: {str(e)}"
            }

    def update_user_profile(self, profile_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 프로필 업데이트

        Args:
            profile_id (str): 업데이트할 프로필 ID
            update_data (Dict[str, Any]): 업데이트할 데이터

        Returns:
            Dict[str, Any]: 업데이트 결과
        """
        try:
            collection = self.get_collection("user_profiles")

            # 업데이트 시간 추가
            update_data["updated_at"] = datetime.now()

            result = collection.update_one(
                {"profile_id": profile_id, "is_active": True},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"업데이트할 프로필을 찾을 수 없습니다: {profile_id}"
                }

            return {
                "success": True,
                "modified_count": result.modified_count,
                "message": "프로필이 성공적으로 업데이트되었습니다."
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"프로필 업데이트 중 오류가 발생했습니다: {str(e)}"
            }

    # === 정책 관련 메서드 ===

    def save_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        정책 저장

        Args:
            policy_data (Dict[str, Any]): 저장할 정책 데이터

        Returns:
            Dict[str, Any]: 저장 결과
        """
        try:
            collection = self.get_collection("policies")

            # PolicyDB 모델로 검증
            policy = PolicyDB(**policy_data)

            # MongoDB에 저장
            result = collection.insert_one(policy.model_dump(by_alias=True))

            return {
                "success": True,
                "policy_id": policy.policy_id,
                "mongodb_id": str(result.inserted_id),
                "message": "정책이 성공적으로 저장되었습니다."
            }

        except DuplicateKeyError:
            return {
                "success": False,
                "error": f"이미 존재하는 정책 ID입니다: {policy_data.get('policy_id')}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"정책 저장 중 오류가 발생했습니다: {str(e)}"
            }

    def save_multiple_policies(self, policies_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 정책 일괄 저장

        Args:
            policies_data (List[Dict[str, Any]]): 저장할 정책 데이터 목록

        Returns:
            Dict[str, Any]: 저장 결과
        """
        try:
            collection = self.get_collection("policies")

            # 모든 정책 데이터를 PolicyDB 모델로 검증
            validated_policies = []
            for policy_data in policies_data:
                policy = PolicyDB(**policy_data)
                validated_policies.append(policy.model_dump(by_alias=True))

            # 일괄 삽입
            result = collection.insert_many(validated_policies, ordered=False)

            return {
                "success": True,
                "inserted_count": len(result.inserted_ids),
                "inserted_ids": [str(id) for id in result.inserted_ids],
                "message": f"{len(result.inserted_ids)}개의 정책이 성공적으로 저장되었습니다."
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"정책 일괄 저장 중 오류가 발생했습니다: {str(e)}"
            }

    def get_all_policies(self, active_only: bool = True) -> Dict[str, Any]:
        """
        전체 정책 조회

        Args:
            active_only (bool): 활성 정책만 조회할지 여부

        Returns:
            Dict[str, Any]: 조회 결과
        """
        try:
            collection = self.get_collection("policies")

            query = {"is_active": True} if active_only else {}
            policies = list(collection.find(query).sort("created_at", DESCENDING))

            # ObjectId를 문자열로 변환
            for policy in policies:
                policy["_id"] = str(policy["_id"])

            return {
                "success": True,
                "policies": policies,
                "count": len(policies),
                "message": "정책 조회 완료"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"정책 조회 중 오류가 발생했습니다: {str(e)}"
            }

    def get_policies_by_category(self, category: str, active_only: bool = True) -> Dict[str, Any]:
        """
        카테고리별 정책 조회

        Args:
            category (str): 정책 카테고리
            active_only (bool): 활성 정책만 조회할지 여부

        Returns:
            Dict[str, Any]: 조회 결과
        """
        try:
            collection = self.get_collection("policies")

            query = {"category": category}
            if active_only:
                query["is_active"] = True

            policies = list(collection.find(query).sort("created_at", DESCENDING))

            # ObjectId를 문자열로 변환
            for policy in policies:
                policy["_id"] = str(policy["_id"])

            return {
                "success": True,
                "policies": policies,
                "category": category,
                "count": len(policies),
                "message": f"'{category}' 카테고리 정책 조회 완료"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"카테고리별 정책 조회 중 오류가 발생했습니다: {str(e)}"
            }

    # === 추천 관련 메서드 ===

    def save_recommendation(self, user_profile_id: str, recommendations: List[Dict[str, Any]],
                          agent_used: str = "Agent2", **kwargs) -> Dict[str, Any]:
        """
        추천 이력 저장

        Args:
            user_profile_id (str): 사용자 프로필 ID
            recommendations (List[Dict[str, Any]]): 추천된 정책 목록
            agent_used (str): 추천에 사용된 Agent
            **kwargs: 추가 추천 정보

        Returns:
            Dict[str, Any]: 저장 결과
        """
        try:
            collection = self.get_collection("recommendations")

            recommendation_data = {
                "recommendation_id": f"rec_{uuid.uuid4().hex[:8]}",
                "user_profile_id": user_profile_id,
                "recommended_policies": recommendations,
                "agent_used": agent_used,
                **kwargs
            }

            # RecommendationDB 모델로 검증
            recommendation = RecommendationDB(**recommendation_data)

            # MongoDB에 저장
            result = collection.insert_one(recommendation.model_dump(by_alias=True))

            return {
                "success": True,
                "recommendation_id": recommendation.recommendation_id,
                "mongodb_id": str(result.inserted_id),
                "message": "추천 이력이 성공적으로 저장되었습니다."
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"추천 이력 저장 중 오류가 발생했습니다: {str(e)}"
            }

    def get_user_recommendations(self, user_profile_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        사용자의 추천 이력 조회

        Args:
            user_profile_id (str): 사용자 프로필 ID
            limit (int): 조회할 최대 개수

        Returns:
            Dict[str, Any]: 조회 결과
        """
        try:
            collection = self.get_collection("recommendations")

            recommendations = list(
                collection.find({"user_profile_id": user_profile_id})
                .sort("created_at", DESCENDING)
                .limit(limit)
            )

            # ObjectId를 문자열로 변환
            for rec in recommendations:
                rec["_id"] = str(rec["_id"])

            return {
                "success": True,
                "recommendations": recommendations,
                "count": len(recommendations),
                "message": "추천 이력 조회 완료"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"추천 이력 조회 중 오류가 발생했습니다: {str(e)}"
            }

    # === 세션 관리 메서드 ===

    def create_session(self, user_profile_id: str, session_duration_hours: int = 24) -> Dict[str, Any]:
        """
        사용자 세션 생성

        Args:
            user_profile_id (str): 사용자 프로필 ID
            session_duration_hours (int): 세션 지속 시간 (시간)

        Returns:
            Dict[str, Any]: 생성 결과
        """
        try:
            collection = self.get_collection("user_sessions")

            session_data = {
                "session_id": f"session_{uuid.uuid4().hex[:8]}",
                "user_profile_id": user_profile_id,
                "expires_at": datetime.now() + timedelta(hours=session_duration_hours)
            }

            session = UserSessionDB(**session_data)
            result = collection.insert_one(session.model_dump(by_alias=True))

            return {
                "success": True,
                "session_id": session.session_id,
                "expires_at": session.expires_at.isoformat(),
                "message": "세션이 생성되었습니다."
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"세션 생성 중 오류가 발생했습니다: {str(e)}"
            }

    def close(self) -> None:
        """MongoDB 연결 종료"""
        try:
            if self.client:
                self.client.close()
                self.is_connected = False
                print("✅ MongoDB 연결이 종료되었습니다.")
        except Exception as e:
            print(f"⚠️ MongoDB 연결 종료 중 오류: {e}")

    def __del__(self):
        """소멸자: 연결 정리"""
        self.close()


# 전역 MongoDB 핸들러 인스턴스 (싱글톤 패턴)
_mongodb_handler_instance: Optional[MongoDBHandler] = None


def get_mongodb_handler() -> MongoDBHandler:
    """
    MongoDB 핸들러 싱글톤 인스턴스 반환

    Returns:
        MongoDBHandler: MongoDB 핸들러 인스턴스
    """
    global _mongodb_handler_instance

    if _mongodb_handler_instance is None:
        _mongodb_handler_instance = MongoDBHandler()

    return _mongodb_handler_instance


if __name__ == "__main__":
    """MongoDB 연결 테스트"""
    print("🔍 MongoDB 핸들러 테스트 시작...")
    print("=" * 50)

    # MongoDB 핸들러 생성
    handler = MongoDBHandler()

    # 연결 테스트
    print("\n📡 MongoDB 연결 테스트")
    connection_result = handler.test_connection()
    print(f"연결 상태: {connection_result}")

    if connection_result.get("connected"):
        print("\n✅ MongoDB 핸들러 테스트 완료!")
    else:
        print("\n❌ MongoDB 연결 실패. 환경변수를 확인하세요.")

    # 연결 종료
    handler.close()