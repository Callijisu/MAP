"""
청년 정책 추천 시스템 - 설정 관리
환경 변수와 애플리케이션 설정을 중앙화하여 관리
"""

import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""

    # === 기본 애플리케이션 설정 ===
    app_name: str = Field(default="청년 정책 추천 시스템", description="애플리케이션 이름")
    app_version: str = Field(default="1.0.0", description="애플리케이션 버전")
    debug: bool = Field(default=False, description="디버그 모드")
    environment: str = Field(default="development", description="실행 환경 (development/production)")

    # === 서버 설정 ===
    host: str = Field(default="0.0.0.0", description="서버 호스트")
    port: int = Field(default=8000, description="서버 포트")
    reload: bool = Field(default=True, description="자동 리로드 여부")

    # === 데이터베이스 설정 ===
    mongodb_uri: Optional[str] = Field(default=None, description="MongoDB 연결 URI")
    database_name: str = Field(default="youth_policy", description="데이터베이스 이름")
    mongodb_timeout: int = Field(default=10000, description="MongoDB 연결 타임아웃 (ms)")

    # === 외부 API 설정 ===
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API 키")
    openai_model: str = Field(default="gpt-4", description="OpenAI 모델명")
    openai_max_tokens: int = Field(default=1000, description="OpenAI 최대 토큰 수")
    openai_temperature: float = Field(default=0.7, description="OpenAI Temperature")

    # === 로깅 설정 ===
    log_level: str = Field(default="INFO", description="로그 레벨")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="로그 포맷"
    )
    log_file: Optional[str] = Field(default=None, description="로그 파일 경로")
    log_max_bytes: int = Field(default=10485760, description="로그 파일 최대 크기 (10MB)")
    log_backup_count: int = Field(default=5, description="로그 백업 파일 수")

    # === CORS 설정 ===
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="허용된 CORS 오리진"
    )
    cors_allow_credentials: bool = Field(default=True, description="CORS 인증 정보 허용")
    cors_allow_methods: List[str] = Field(default=["*"], description="허용된 HTTP 메소드")
    cors_allow_headers: List[str] = Field(default=["*"], description="허용된 HTTP 헤더")

    # === 보안 설정 ===
    secret_key: str = Field(default="your-secret-key-here", description="비밀 키")
    algorithm: str = Field(default="HS256", description="암호화 알고리즘")
    access_token_expire_minutes: int = Field(default=30, description="액세스 토큰 만료 시간 (분)")

    # === 캐시 설정 ===
    cache_ttl: int = Field(default=3600, description="캐시 TTL (초)")
    cache_max_size: int = Field(default=1000, description="캐시 최대 크기")

    # === Agent 설정 ===
    agent_timeout: float = Field(default=30.0, description="Agent 실행 타임아웃 (초)")
    max_policy_results: int = Field(default=50, description="최대 정책 결과 수")
    min_matching_score: float = Field(default=40.0, description="최소 매칭 점수")

    # === API 제한 설정 ===
    api_rate_limit: str = Field(default="100/minute", description="API 요청 제한")
    max_request_size: int = Field(default=1048576, description="최대 요청 크기 (1MB)")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

    @field_validator("mongodb_uri")
    def validate_mongodb_uri(cls, v):
        """MongoDB URI 검증"""
        if v and not (v.startswith("mongodb://") or v.startswith("mongodb+srv://")):
            raise ValueError("MongoDB URI는 mongodb:// 또는 mongodb+srv://로 시작해야 합니다")
        return v

    @field_validator("log_level")
    def validate_log_level(cls, v):
        """로그 레벨 검증"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"로그 레벨은 다음 중 하나여야 합니다: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("port")
    def validate_port(cls, v):
        """포트 번호 검증"""
        if not 1 <= v <= 65535:
            raise ValueError("포트 번호는 1-65535 범위여야 합니다")
        return v

    @field_validator("openai_temperature")
    def validate_temperature(cls, v):
        """OpenAI Temperature 검증"""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature는 0.0-2.0 범위여야 합니다")
        return v

    @field_validator("min_matching_score")
    def validate_matching_score(cls, v):
        """매칭 점수 검증"""
        if not 0.0 <= v <= 100.0:
            raise ValueError("매칭 점수는 0.0-100.0 범위여야 합니다")
        return v

    def is_development(self) -> bool:
        """개발 환경 여부 확인"""
        return self.environment.lower() in ["development", "dev", "local"]

    def is_production(self) -> bool:
        """프로덕션 환경 여부 확인"""
        return self.environment.lower() in ["production", "prod"]

    def get_mongodb_config(self) -> dict:
        """MongoDB 설정 반환"""
        return {
            "uri": self.mongodb_uri,
            "database": self.database_name,
            "timeout": self.mongodb_timeout
        }

    def get_openai_config(self) -> dict:
        """OpenAI 설정 반환"""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "max_tokens": self.openai_max_tokens,
            "temperature": self.openai_temperature
        }

    def get_cors_config(self) -> dict:
        """CORS 설정 반환"""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_allow_methods,
            "allow_headers": self.cors_allow_headers
        }

    def get_logging_config(self) -> dict:
        """로깅 설정 반환"""
        return {
            "level": self.log_level,
            "format": self.log_format,
            "file": self.log_file,
            "max_bytes": self.log_max_bytes,
            "backup_count": self.log_backup_count
        }


class DatabaseSettings(BaseSettings):
    """데이터베이스 전용 설정"""

    # 연결 설정
    uri: Optional[str] = Field(default=None, env="MONGODB_URI")
    database: str = Field(default="youth_policy", env="DATABASE_NAME")

    # 연결 풀 설정
    min_pool_size: int = Field(default=0, description="최소 연결 풀 크기")
    max_pool_size: int = Field(default=100, description="최대 연결 풀 크기")
    max_idle_time_ms: int = Field(default=30000, description="최대 유휴 시간 (ms)")

    # 타임아웃 설정
    connect_timeout_ms: int = Field(default=10000, description="연결 타임아웃 (ms)")
    server_selection_timeout_ms: int = Field(default=30000, description="서버 선택 타임아웃 (ms)")
    socket_timeout_ms: int = Field(default=10000, description="소켓 타임아웃 (ms)")

    # 인덱스 설정
    auto_create_indexes: bool = Field(default=True, description="자동 인덱스 생성")
    index_creation_timeout: int = Field(default=60, description="인덱스 생성 타임아웃 (초)")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


class SecuritySettings(BaseSettings):
    """보안 관련 설정"""

    # 암호화 설정
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", description="JWT 알고리즘")

    # 토큰 설정
    access_token_expire_minutes: int = Field(default=30, description="액세스 토큰 만료 시간")
    refresh_token_expire_days: int = Field(default=7, description="리프레시 토큰 만료 시간")

    # API 보안 설정
    api_key_header: str = Field(default="X-API-Key", description="API 키 헤더")
    max_request_size: int = Field(default=1048576, description="최대 요청 크기 (1MB)")
    rate_limit_per_minute: int = Field(default=100, description="분당 요청 제한")

    # 입력 검증 설정
    max_string_length: int = Field(default=1000, description="최대 문자열 길이")
    max_list_length: int = Field(default=100, description="최대 리스트 길이")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


class CacheSettings(BaseSettings):
    """캐시 관련 설정"""

    # Redis 설정 (미래 확장용)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    redis_db: int = Field(default=0, description="Redis 데이터베이스 번호")

    # 메모리 캐시 설정
    memory_cache_ttl: int = Field(default=3600, description="메모리 캐시 TTL (초)")
    memory_cache_max_size: int = Field(default=1000, description="메모리 캐시 최대 크기")

    # GPT 응답 캐시 설정
    gpt_cache_enabled: bool = Field(default=True, description="GPT 캐시 활성화")
    gpt_cache_ttl: int = Field(default=86400, description="GPT 캐시 TTL (24시간)")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """
    설정 인스턴스를 캐시와 함께 반환
    애플리케이션에서 설정을 사용할 때 이 함수를 호출
    """
    return Settings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """데이터베이스 설정 인스턴스 반환"""
    return DatabaseSettings()


@lru_cache()
def get_security_settings() -> SecuritySettings:
    """보안 설정 인스턴스 반환"""
    return SecuritySettings()


@lru_cache()
def get_cache_settings() -> CacheSettings:
    """캐시 설정 인스턴스 반환"""
    return CacheSettings()


# 환경별 설정 로더
def load_settings_for_environment(env: str = None) -> Settings:
    """
    특정 환경에 맞는 설정 로드

    Args:
        env: 환경 이름 (development, production, test)

    Returns:
        Settings: 설정 인스턴스
    """
    if env:
        os.environ["ENVIRONMENT"] = env

    settings = Settings()

    # 환경별 특별 설정
    if settings.is_production():
        # 프로덕션 환경에서는 디버그 모드 비활성화
        settings.debug = False
        settings.reload = False
        settings.log_level = "WARNING"

    elif settings.is_development():
        # 개발 환경에서는 디버그 모드 활성화
        settings.debug = True
        settings.reload = True
        settings.log_level = "DEBUG"

    return settings


# 설정 검증 함수
def validate_settings() -> bool:
    """
    설정 유효성 검증

    Returns:
        bool: 설정이 유효한지 여부
    """
    try:
        settings = get_settings()

        # 필수 설정 확인
        if not settings.secret_key or settings.secret_key == "your-secret-key-here":
            print("⚠️ SECRET_KEY가 기본값으로 설정되어 있습니다. 보안을 위해 변경하세요.")

        if not settings.mongodb_uri:
            print("⚠️ MONGODB_URI가 설정되지 않았습니다. 로컬 모드로 실행됩니다.")

        if not settings.openai_api_key:
            print("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. GPT 기능이 제한됩니다.")

        print(f"✅ 설정 검증 완료 (환경: {settings.environment})")
        return True

    except Exception as e:
        print(f"❌ 설정 검증 실패: {e}")
        return False


# 설정 정보 출력 함수
def print_settings_summary():
    """설정 요약 정보 출력"""
    try:
        settings = get_settings()

        print("\n🔧 === 청년 정책 추천 시스템 설정 ===")
        print(f"📱 애플리케이션: {settings.app_name} v{settings.app_version}")
        print(f"🌍 환경: {settings.environment}")
        print(f"🔧 디버그 모드: {settings.debug}")
        print(f"🌐 서버: {settings.host}:{settings.port}")
        print(f"📊 데이터베이스: {'✅ 연결됨' if settings.mongodb_uri else '❌ 미연결 (로컬 모드)'}")
        print(f"🤖 OpenAI: {'✅ 설정됨' if settings.openai_api_key else '❌ 미설정 (Fallback 모드)'}")
        print(f"📝 로그 레벨: {settings.log_level}")
        print("==========================================\n")

    except Exception as e:
        print(f"❌ 설정 정보 출력 실패: {e}")


if __name__ == "__main__":
    """설정 모듈 직접 실행 시 검증 및 정보 출력"""
    print("🚀 청년 정책 추천 시스템 - 설정 검증")

    if validate_settings():
        print_settings_summary()
    else:
        exit(1)