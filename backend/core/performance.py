"""
청년 정책 추천 시스템 - 성능 최적화 모듈
MongoDB 인덱스 관리, 캐싱, 성능 모니터링 기능 제공
"""

import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
from collections import defaultdict, OrderedDict
import threading
import asyncio

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import OperationFailure
from .logging import get_logger, get_database_logger

logger = get_logger("performance")
db_logger = get_database_logger()


class LRUCache:
    """메모리 효율적인 LRU 캐시 구현"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        LRU 캐시 초기화

        Args:
            max_size: 최대 캐시 크기
            ttl: Time To Live (초)
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        with self.lock:
            if key in self.cache:
                # TTL 확인
                if time.time() - self.timestamps[key] > self.ttl:
                    del self.cache[key]
                    del self.timestamps[key]
                    return None

                # LRU 업데이트
                self.cache.move_to_end(key)
                return self.cache[key]
            return None

    def put(self, key: str, value: Any):
        """캐시에 값 저장"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.max_size:
                    # 가장 오래된 항목 제거
                    oldest = next(iter(self.cache))
                    del self.cache[oldest]
                    del self.timestamps[oldest]

            self.cache[key] = value
            self.timestamps[key] = time.time()

    def clear(self):
        """캐시 초기화"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()

    def size(self) -> int:
        """현재 캐시 크기"""
        return len(self.cache)

    def stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        with self.lock:
            current_time = time.time()
            expired_count = sum(
                1 for ts in self.timestamps.values()
                if current_time - ts > self.ttl
            )
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "expired_items": expired_count,
                "ttl": self.ttl
            }


class CacheManager:
    """통합 캐시 관리자"""

    def __init__(self):
        self.caches = {
            "policies": LRUCache(max_size=500, ttl=3600),      # 정책 데이터
            "profiles": LRUCache(max_size=1000, ttl=1800),     # 프로필 데이터
            "gpt_responses": LRUCache(max_size=200, ttl=86400), # GPT 응답
            "matching_results": LRUCache(max_size=500, ttl=1800) # 매칭 결과
        }
        self.hit_count = defaultdict(int)
        self.miss_count = defaultdict(int)

    def get_cache(self, cache_name: str) -> LRUCache:
        """특정 캐시 인스턴스 반환"""
        if cache_name not in self.caches:
            self.caches[cache_name] = LRUCache()
        return self.caches[cache_name]

    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        cache = self.get_cache(cache_name)
        value = cache.get(key)

        if value is not None:
            self.hit_count[cache_name] += 1
            logger.debug(f"캐시 히트: {cache_name}:{key}")
        else:
            self.miss_count[cache_name] += 1
            logger.debug(f"캐시 미스: {cache_name}:{key}")

        return value

    def put(self, cache_name: str, key: str, value: Any):
        """캐시에 값 저장"""
        cache = self.get_cache(cache_name)
        cache.put(key, value)
        logger.debug(f"캐시 저장: {cache_name}:{key}")

    def invalidate(self, cache_name: str, key: Optional[str] = None):
        """캐시 무효화"""
        cache = self.get_cache(cache_name)
        if key is None:
            cache.clear()
            logger.info(f"캐시 전체 삭제: {cache_name}")
        else:
            if key in cache.cache:
                del cache.cache[key]
                del cache.timestamps[key]
                logger.info(f"캐시 삭제: {cache_name}:{key}")

    def get_stats(self) -> Dict[str, Any]:
        """전체 캐시 통계"""
        stats = {}
        for cache_name, cache in self.caches.items():
            cache_stats = cache.stats()
            cache_stats.update({
                "hits": self.hit_count[cache_name],
                "misses": self.miss_count[cache_name],
                "hit_rate": (
                    self.hit_count[cache_name] /
                    (self.hit_count[cache_name] + self.miss_count[cache_name])
                    if (self.hit_count[cache_name] + self.miss_count[cache_name]) > 0
                    else 0
                )
            })
            stats[cache_name] = cache_stats
        return stats


# 전역 캐시 매니저
cache_manager = CacheManager()


def create_cache_key(*args, **kwargs) -> str:
    """캐시 키 생성"""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(cache_name: str, ttl: Optional[int] = None):
    """캐싱 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{create_cache_key(*args, **kwargs)}"

            # 캐시 조회
            result = cache_manager.get(cache_name, cache_key)
            if result is not None:
                return result

            # 함수 실행 및 캐시 저장
            result = func(*args, **kwargs)
            cache_manager.put(cache_name, cache_key, result)
            return result

        return wrapper
    return decorator


class MongoIndexManager:
    """MongoDB 인덱스 관리자"""

    def __init__(self, mongo_handler):
        """
        인덱스 매니저 초기화

        Args:
            mongo_handler: MongoDBHandler 인스턴스
        """
        self.mongo_handler = mongo_handler
        self.db_logger = get_database_logger()

    def create_policy_indexes(self):
        """정책 컬렉션 인덱스 생성"""
        try:
            policies_collection = self.mongo_handler.get_collection("policies")

            # 복합 인덱스들
            indexes = [
                # 카테고리 인덱스
                [("category", ASCENDING)],

                # 지역 인덱스
                [("target_regions", ASCENDING)],

                # 연령 범위 인덱스
                [("target_age_min", ASCENDING), ("target_age_max", ASCENDING)],

                # 고용 상태 인덱스
                [("target_employment", ASCENDING)],

                # 복합 검색 인덱스 (카테고리 + 지역)
                [("category", ASCENDING), ("target_regions", ASCENDING)],

                # 복합 검색 인덱스 (카테고리 + 연령)
                [("category", ASCENDING), ("target_age_min", ASCENDING), ("target_age_max", ASCENDING)],

                # 텍스트 검색 인덱스
                [("title", TEXT), ("benefit", TEXT), ("description", TEXT)],

                # 정렬용 인덱스
                [("created_at", DESCENDING)],
                [("updated_at", DESCENDING)],

                # 정책 ID 고유 인덱스
                [("policy_id", ASCENDING)]
            ]

            created_indexes = []
            for index_fields in indexes:
                try:
                    index_name = policies_collection.create_index(index_fields)
                    created_indexes.append(index_name)
                    self.db_logger.info(
                        f"정책 인덱스 생성 완료: {index_fields}",
                        extra_collection="policies",
                        extra_index=str(index_fields)
                    )
                except Exception as e:
                    self.db_logger.warning(
                        f"정책 인덱스 생성 실패: {index_fields} - {e}",
                        extra_collection="policies",
                        extra_error=str(e)
                    )

            return created_indexes

        except Exception as e:
            self.db_logger.error(f"정책 인덱스 생성 전체 실패: {e}")
            return []

    def create_profile_indexes(self):
        """프로필 컬렉션 인덱스 생성"""
        try:
            profiles_collection = self.mongo_handler.get_collection("user_profiles")

            indexes = [
                # 프로필 ID 고유 인덱스
                [("profile_id", ASCENDING)],

                # 사용자 검색 인덱스
                [("age", ASCENDING)],
                [("region", ASCENDING)],
                [("employment", ASCENDING)],
                [("income", ASCENDING)],

                # 복합 검색 인덱스
                [("age", ASCENDING), ("region", ASCENDING)],
                [("region", ASCENDING), ("employment", ASCENDING)],

                # 시간 인덱스
                [("created_at", DESCENDING)],
                [("updated_at", DESCENDING)]
            ]

            created_indexes = []
            for index_fields in indexes:
                try:
                    index_name = profiles_collection.create_index(index_fields)
                    created_indexes.append(index_name)
                    self.db_logger.info(
                        f"프로필 인덱스 생성 완료: {index_fields}",
                        extra_collection="user_profiles",
                        extra_index=str(index_fields)
                    )
                except Exception as e:
                    self.db_logger.warning(
                        f"프로필 인덱스 생성 실패: {index_fields} - {e}",
                        extra_collection="user_profiles",
                        extra_error=str(e)
                    )

            return created_indexes

        except Exception as e:
            self.db_logger.error(f"프로필 인덱스 생성 전체 실패: {e}")
            return []

    def create_recommendation_indexes(self):
        """추천 이력 컬렉션 인덱스 생성"""
        try:
            recommendations_collection = self.mongo_handler.get_collection("recommendations")

            indexes = [
                # 사용자별 추천 이력 조회 인덱스
                [("user_id", ASCENDING), ("created_at", DESCENDING)],

                # 세션 ID 인덱스
                [("session_id", ASCENDING)],

                # 시간 기반 인덱스
                [("created_at", DESCENDING)],

                # 성능 분석용 인덱스
                [("avg_score", DESCENDING)],
                [("total_recommendations", DESCENDING)]
            ]

            created_indexes = []
            for index_fields in indexes:
                try:
                    index_name = recommendations_collection.create_index(index_fields)
                    created_indexes.append(index_name)
                    self.db_logger.info(
                        f"추천 인덱스 생성 완료: {index_fields}",
                        extra_collection="recommendations",
                        extra_index=str(index_fields)
                    )
                except Exception as e:
                    self.db_logger.warning(
                        f"추천 인덱스 생성 실패: {index_fields} - {e}",
                        extra_collection="recommendations",
                        extra_error=str(e)
                    )

            return created_indexes

        except Exception as e:
            self.db_logger.error(f"추천 인덱스 생성 전체 실패: {e}")
            return []

    def create_all_indexes(self):
        """모든 인덱스 생성"""
        logger.info("MongoDB 인덱스 생성 시작")
        start_time = time.time()

        results = {
            "policies": self.create_policy_indexes(),
            "profiles": self.create_profile_indexes(),
            "recommendations": self.create_recommendation_indexes()
        }

        end_time = time.time()
        duration = end_time - start_time

        total_indexes = sum(len(indexes) for indexes in results.values())
        logger.info(
            f"MongoDB 인덱스 생성 완료: {total_indexes}개 ({duration:.3f}초)",
            extra_duration=duration,
            extra_total_indexes=total_indexes
        )

        return results

    def list_indexes(self, collection_name: str) -> List[Dict]:
        """컬렉션의 모든 인덱스 조회"""
        try:
            collection = self.mongo_handler.get_collection(collection_name)
            return list(collection.list_indexes())
        except Exception as e:
            self.db_logger.error(f"인덱스 조회 실패: {collection_name} - {e}")
            return []

    def drop_index(self, collection_name: str, index_name: str):
        """특정 인덱스 삭제"""
        try:
            collection = self.mongo_handler.get_collection(collection_name)
            collection.drop_index(index_name)
            self.db_logger.info(f"인덱스 삭제 완료: {collection_name}.{index_name}")
        except Exception as e:
            self.db_logger.error(f"인덱스 삭제 실패: {collection_name}.{index_name} - {e}")


class PerformanceMonitor:
    """성능 모니터링 클래스"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_times = {}

    def start_timer(self, operation: str) -> str:
        """타이머 시작"""
        timer_id = f"{operation}_{int(time.time() * 1000)}"
        self.start_times[timer_id] = time.time()
        return timer_id

    def end_timer(self, timer_id: str) -> float:
        """타이머 종료 및 소요 시간 반환"""
        if timer_id in self.start_times:
            duration = time.time() - self.start_times[timer_id]
            del self.start_times[timer_id]
            return duration
        return 0.0

    def record_metric(self, operation: str, duration: float, **metadata):
        """성능 메트릭 기록"""
        metric = {
            "timestamp": datetime.now(),
            "duration": duration,
            **metadata
        }
        self.metrics[operation].append(metric)

        # 최근 1000개만 유지
        if len(self.metrics[operation]) > 1000:
            self.metrics[operation] = self.metrics[operation][-1000:]

    def get_stats(self, operation: str = None) -> Dict[str, Any]:
        """성능 통계 조회"""
        if operation:
            if operation not in self.metrics:
                return {}

            durations = [m["duration"] for m in self.metrics[operation]]
            return {
                "operation": operation,
                "count": len(durations),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "total_duration": sum(durations)
            }
        else:
            # 전체 통계
            stats = {}
            for op, metrics in self.metrics.items():
                durations = [m["duration"] for m in metrics]
                stats[op] = {
                    "count": len(durations),
                    "avg_duration": sum(durations) / len(durations) if durations else 0,
                    "min_duration": min(durations) if durations else 0,
                    "max_duration": max(durations) if durations else 0,
                    "total_duration": sum(durations) if durations else 0
                }
            return stats

    def clear_metrics(self):
        """모든 메트릭 초기화"""
        self.metrics.clear()
        self.start_times.clear()


# 전역 성능 모니터
performance_monitor = PerformanceMonitor()


def monitor_performance(operation: str):
    """성능 모니터링 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            timer_id = performance_monitor.start_timer(operation)
            try:
                result = func(*args, **kwargs)
                duration = performance_monitor.end_timer(timer_id)
                performance_monitor.record_metric(
                    operation,
                    duration,
                    success=True,
                    function=func.__name__
                )
                return result
            except Exception as e:
                duration = performance_monitor.end_timer(timer_id)
                performance_monitor.record_metric(
                    operation,
                    duration,
                    success=False,
                    error=str(e),
                    function=func.__name__
                )
                raise
        return wrapper
    return decorator


class DatabaseQueryOptimizer:
    """데이터베이스 쿼리 최적화"""

    @staticmethod
    def optimize_policy_query(filters: Dict[str, Any]) -> Dict[str, Any]:
        """정책 쿼리 최적화"""
        optimized_query = {}

        # 카테고리 필터
        if "category" in filters:
            optimized_query["category"] = filters["category"]

        # 지역 필터
        if "region" in filters:
            optimized_query["target_regions"] = {"$in": [filters["region"], "전국"]}

        # 나이 필터
        if "age" in filters:
            age = filters["age"]
            optimized_query["$and"] = [
                {"target_age_min": {"$lte": age}},
                {"target_age_max": {"$gte": age}}
            ]

        # 고용 상태 필터
        if "employment" in filters:
            optimized_query["target_employment"] = {"$in": [filters["employment"]]}

        # 소득 필터
        if "income" in filters:
            optimized_query["$or"] = [
                {"target_income_max": {"$gte": filters["income"]}},
                {"target_income_max": None}  # 소득 제한 없음
            ]

        return optimized_query

    @staticmethod
    def create_aggregation_pipeline(query: Dict, sort_field: str = None, limit: int = None) -> List[Dict]:
        """집계 파이프라인 생성"""
        pipeline = []

        # Match 스테이지
        if query:
            pipeline.append({"$match": query})

        # Sort 스테이지
        if sort_field:
            pipeline.append({"$sort": {sort_field: -1}})

        # Limit 스테이지
        if limit:
            pipeline.append({"$limit": limit})

        # 필요한 필드만 선택
        pipeline.append({
            "$project": {
                "_id": 0,
                "policy_id": 1,
                "title": 1,
                "category": 1,
                "target_age_min": 1,
                "target_age_max": 1,
                "target_regions": 1,
                "target_employment": 1,
                "target_income_max": 1,
                "benefit": 1,
                "budget_max": 1,
                "deadline": 1,
                "application_url": 1
            }
        })

        return pipeline


def setup_performance_optimizations(mongo_handler):
    """성능 최적화 설정"""
    try:
        logger.info("성능 최적화 설정 시작")

        # 인덱스 생성
        index_manager = MongoIndexManager(mongo_handler)
        index_results = index_manager.create_all_indexes()

        # 캐시 초기화
        cache_manager.invalidate("policies")
        cache_manager.invalidate("profiles")

        logger.info(
            "성능 최적화 설정 완료",
            extra_indexes_created=sum(len(indexes) for indexes in index_results.values()),
            extra_cache_initialized=True
        )

        return True

    except Exception as e:
        logger.error(f"성능 최적화 설정 실패: {e}")
        return False


def get_performance_stats() -> Dict[str, Any]:
    """전체 성능 통계 조회"""
    return {
        "cache_stats": cache_manager.get_stats(),
        "performance_stats": performance_monitor.get_stats(),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    """성능 최적화 모듈 테스트"""
    print("🚀 청년 정책 추천 시스템 - 성능 최적화 모듈 테스트")

    # 캐시 테스트
    cache_manager.put("test", "key1", {"data": "value1"})
    cached_value = cache_manager.get("test", "key1")
    print(f"캐시 테스트: {cached_value}")

    # 성능 모니터링 테스트
    timer_id = performance_monitor.start_timer("test_operation")
    time.sleep(0.1)  # 0.1초 대기
    duration = performance_monitor.end_timer(timer_id)
    performance_monitor.record_metric("test_operation", duration)

    stats = performance_monitor.get_stats("test_operation")
    print(f"성능 통계: {stats}")

    print("✅ 성능 최적화 모듈 테스트 완료")