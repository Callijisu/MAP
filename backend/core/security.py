"""
청년 정책 추천 시스템 - 보안 강화 모듈
입력 검증, SQL Injection 방지, 레이트 제한 등 보안 기능 제공
"""

import re
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from collections import defaultdict
import bleach
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import jwt  # JWT 기능은 필요시 추가

from .config import get_security_settings
from .logging import get_logger

logger = get_logger("security")
security_settings = get_security_settings()


class SecurityValidationError(Exception):
    """보안 검증 실패 예외"""
    pass


class InputSanitizer:
    """입력 데이터 정화 클래스"""

    # 허용된 HTML 태그 (매우 제한적)
    ALLOWED_TAGS = []
    ALLOWED_ATTRIBUTES = {}

    # 위험한 패턴들
    DANGEROUS_PATTERNS = [
        # SQL Injection 패턴
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        # NoSQL Injection 패턴
        r"(\$where|\$ne|\$gt|\$lt|\$regex|\$or|\$and)",
        # Script 태그
        r"<script[^>]*>.*?</script>",
        # JavaScript 이벤트
        r"on\w+\s*=",
        # 파일 경로 조작
        r"(\.\./|\.\.\\|\.\./\.\./)",
        # 명령 실행
        r"(\b(eval|exec|system|shell_exec)\s*\()",
    ]

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """문자열 정화"""
        if not isinstance(value, str):
            raise SecurityValidationError(f"문자열이 아닌 타입: {type(value)}")

        # 길이 검증
        if len(value) > max_length:
            raise SecurityValidationError(f"문자열 길이 초과: {len(value)} > {max_length}")

        # 위험한 패턴 검사
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"위험한 패턴 감지: {pattern[:20]}...")
                raise SecurityValidationError(f"허용되지 않는 패턴이 포함되어 있습니다")

        # HTML 태그 제거
        sanitized = bleach.clean(
            value,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )

        # 추가 정화
        sanitized = sanitized.strip()

        return sanitized

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """딕셔너리 정화"""
        if max_depth <= 0:
            raise SecurityValidationError("딕셔너리 중첩 깊이 초과")

        sanitized = {}
        for key, value in data.items():
            # 키 정화
            clean_key = cls.sanitize_string(key, max_length=100)

            # 값 정화
            if isinstance(value, str):
                clean_value = cls.sanitize_string(value)
            elif isinstance(value, dict):
                clean_value = cls.sanitize_dict(value, max_depth - 1)
            elif isinstance(value, list):
                clean_value = cls.sanitize_list(value, max_depth - 1)
            elif isinstance(value, (int, float, bool)) or value is None:
                clean_value = value
            else:
                raise SecurityValidationError(f"지원되지 않는 데이터 타입: {type(value)}")

            sanitized[clean_key] = clean_value

        return sanitized

    @classmethod
    def sanitize_list(cls, data: List[Any], max_depth: int = 5) -> List[Any]:
        """리스트 정화"""
        if len(data) > security_settings.max_list_length:
            raise SecurityValidationError(f"리스트 길이 초과: {len(data)} > {security_settings.max_list_length}")

        sanitized = []
        for item in data:
            if isinstance(item, str):
                clean_item = cls.sanitize_string(item)
            elif isinstance(item, dict):
                clean_item = cls.sanitize_dict(item, max_depth - 1)
            elif isinstance(item, list):
                clean_item = cls.sanitize_list(item, max_depth - 1)
            elif isinstance(item, (int, float, bool)) or item is None:
                clean_item = item
            else:
                raise SecurityValidationError(f"지원되지 않는 데이터 타입: {type(item)}")

            sanitized.append(clean_item)

        return sanitized


class RateLimiter:
    """레이트 리미터 클래스"""

    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = defaultdict(datetime)

    def is_allowed(
        self,
        identifier: str,
        max_requests: int = 100,
        window_minutes: int = 1,
        block_duration_minutes: int = 5
    ) -> bool:
        """요청 허용 여부 확인"""
        now = datetime.now()

        # 차단된 IP 확인
        if identifier in self.blocked_ips:
            if now < self.blocked_ips[identifier]:
                logger.warning(f"차단된 IP에서 요청: {identifier}")
                return False
            else:
                # 차단 해제
                del self.blocked_ips[identifier]

        # 윈도우 내 요청 수 확인
        window_start = now - timedelta(minutes=window_minutes)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]

        # 현재 요청 추가
        self.requests[identifier].append(now)

        # 제한 검사
        if len(self.requests[identifier]) > max_requests:
            # IP 차단
            self.blocked_ips[identifier] = now + timedelta(minutes=block_duration_minutes)
            logger.warning(
                f"레이트 제한 초과로 IP 차단: {identifier}",
                extra_requests=len(self.requests[identifier]),
                extra_max_requests=max_requests,
                extra_window_minutes=window_minutes
            )
            return False

        return True

    def get_stats(self, identifier: str = None) -> Dict[str, Any]:
        """레이트 리미터 통계"""
        if identifier:
            return {
                "identifier": identifier,
                "recent_requests": len(self.requests.get(identifier, [])),
                "is_blocked": identifier in self.blocked_ips,
                "block_expires": self.blocked_ips.get(identifier)
            }
        else:
            return {
                "total_tracked_ips": len(self.requests),
                "blocked_ips": len(self.blocked_ips),
                "total_requests": sum(len(reqs) for reqs in self.requests.values())
            }


# 전역 레이트 리미터
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """클라이언트 IP 추출"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


class SecureBaseModel(BaseModel):
    """보안이 강화된 기본 모델"""

    class Config:
        # JSON 스키마에서 예시 제거 (정보 누출 방지)
        schema_extra = {}
        # 추가 필드 허용 안함
        extra = "forbid"
        # 문자열 자동 정리
        str_strip_whitespace = True

    def __init__(self, **data):
        # 입력 데이터 정화
        try:
            if isinstance(data, dict):
                sanitized_data = InputSanitizer.sanitize_dict(data)
            else:
                sanitized_data = data
            super().__init__(**sanitized_data)
        except Exception as e:
            logger.error(f"보안 모델 검증 실패: {e}")
            raise SecurityValidationError(f"입력 데이터 검증 실패: {str(e)}")


class SecureProfileRequest(SecureBaseModel):
    """보안이 강화된 프로필 요청 모델"""

    age: int = Field(..., ge=18, le=39, description="나이 (18-39세)")
    region: str = Field(..., min_length=1, max_length=20, description="거주 지역")
    income: int = Field(..., ge=0, le=100000, description="연소득 (만원, 0-100,000)")
    employment: str = Field(..., min_length=1, max_length=20, description="고용 상태")
    interest: Optional[str] = Field(None, max_length=50, description="관심 분야")

    @validator("region")
    def validate_region(cls, v):
        """지역명 검증"""
        if not v or not v.strip():
            raise ValueError("지역명을 입력해주세요")

        # 한글, 영문, 숫자만 허용
        if not re.match(r"^[가-힣a-zA-Z0-9\s]+$", v):
            raise ValueError("지역명에 허용되지 않는 문자가 포함되어 있습니다")

        return v.strip()

    @validator("employment")
    def validate_employment(cls, v):
        """고용 상태 검증"""
        allowed_values = [
            "재직자", "구직자", "자영업", "프리랜서", "학생",
            "무직", "은퇴", "기타"
        ]
        if v not in allowed_values:
            raise ValueError(f"허용된 고용 상태: {', '.join(allowed_values)}")
        return v

    @validator("interest")
    def validate_interest(cls, v):
        """관심 분야 검증"""
        if v is None:
            return v

        if not re.match(r"^[가-힣a-zA-Z0-9\s]+$", v):
            raise ValueError("관심 분야에 허용되지 않는 문자가 포함되어 있습니다")

        return v.strip()


class SecureQueryParams(SecureBaseModel):
    """보안이 강화된 쿼리 파라미터"""

    category: Optional[str] = Field(None, max_length=20, description="카테고리")
    region: Optional[str] = Field(None, max_length=20, description="지역")
    page: int = Field(1, ge=1, le=1000, description="페이지 번호")
    limit: int = Field(20, ge=1, le=100, description="페이지당 결과 수")

    @validator("category", "region")
    def validate_string_fields(cls, v):
        """문자열 필드 검증"""
        if v is None:
            return v
        if not re.match(r"^[가-힣a-zA-Z0-9\s]+$", v):
            raise ValueError("허용되지 않는 문자가 포함되어 있습니다")
        return v.strip()


def rate_limit(
    max_requests: int = 100,
    window_minutes: int = 1,
    block_duration_minutes: int = 5
):
    """레이트 제한 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Request 객체 찾기
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request:
                client_ip = get_client_ip(request)

                if not rate_limiter.is_allowed(
                    client_ip,
                    max_requests,
                    window_minutes,
                    block_duration_minutes
                ):
                    logger.warning(f"레이트 제한 위반: {client_ip}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def secure_endpoint(func: Callable) -> Callable:
    """보안 엔드포인트 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # 요청 로깅
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request:
                client_ip = get_client_ip(request)
                user_agent = request.headers.get("User-Agent", "Unknown")

                logger.info(
                    f"보안 엔드포인트 접근: {request.method} {request.url.path}",
                    extra_client_ip=client_ip,
                    extra_user_agent=user_agent,
                    extra_endpoint=func.__name__
                )

                # 의심스러운 User-Agent 확인
                suspicious_agents = ["bot", "crawler", "spider", "scraper"]
                if any(agent in user_agent.lower() for agent in suspicious_agents):
                    logger.warning(f"의심스러운 User-Agent: {user_agent}")

            return await func(*args, **kwargs)

        except SecurityValidationError as e:
            logger.error(f"보안 검증 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="입력 데이터가 보안 정책에 위배됩니다."
            )
        except Exception as e:
            logger.error(f"보안 엔드포인트 오류: {e}")
            raise

    return wrapper


class MongoQuerySanitizer:
    """MongoDB 쿼리 정화 클래스"""

    DANGEROUS_OPERATORS = [
        "$where", "$regex", "$expr", "$jsonSchema",
        "$function", "$accumulator", "$mergeObjects"
    ]

    @classmethod
    def sanitize_query(cls, query: Dict[str, Any]) -> Dict[str, Any]:
        """MongoDB 쿼리 정화"""
        if not isinstance(query, dict):
            raise SecurityValidationError("쿼리는 딕셔너리 형태여야 합니다")

        sanitized = {}
        for key, value in query.items():
            # 위험한 연산자 확인
            if any(op in str(key) for op in cls.DANGEROUS_OPERATORS):
                raise SecurityValidationError(f"허용되지 않는 MongoDB 연산자: {key}")

            # 키 정화
            clean_key = InputSanitizer.sanitize_string(key, max_length=100)

            # 값 정화
            if isinstance(value, str):
                clean_value = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                clean_value = cls.sanitize_query(value)
            elif isinstance(value, list):
                clean_value = [
                    InputSanitizer.sanitize_string(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                clean_value = value

            sanitized[clean_key] = clean_value

        return sanitized


def validate_mongo_query(query: Dict[str, Any]) -> Dict[str, Any]:
    """MongoDB 쿼리 검증 및 정화"""
    try:
        return MongoQuerySanitizer.sanitize_query(query)
    except SecurityValidationError:
        logger.error(f"위험한 MongoDB 쿼리 차단: {str(query)[:200]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="허용되지 않는 쿼리입니다."
        )


class APIKeyAuth(HTTPBearer):
    """API 키 인증 클래스"""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.valid_api_keys = set()  # 실제로는 데이터베이스에서 관리

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials:
            # API 키 검증 로직
            api_key = credentials.credentials
            if self.validate_api_key(api_key):
                return api_key
            else:
                logger.warning(f"유효하지 않은 API 키: {api_key[:10]}...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 API 키"
                )
        return None

    def validate_api_key(self, api_key: str) -> bool:
        """API 키 검증"""
        # 실제로는 데이터베이스에서 확인
        return len(api_key) >= 32  # 임시 검증 로직


def generate_secure_token(length: int = 32) -> str:
    """보안 토큰 생성"""
    return secrets.token_urlsafe(length)


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """비밀번호 해시화"""
    if salt is None:
        salt = secrets.token_hex(16)

    # PBKDF2 사용 (더 안전한 해시)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hash_obj.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    try:
        salt, hash_value = hashed.split(':')
        return hash_password(password, salt) == hashed
    except (ValueError, AttributeError):
        return False


def get_security_headers() -> Dict[str, str]:
    """보안 헤더 생성"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }


def audit_log(action: str, user_id: str = None, details: Dict[str, Any] = None):
    """감사 로그 기록"""
    logger.info(
        f"감사 로그: {action}",
        extra_action=action,
        extra_user_id=user_id,
        extra_details=details,
        extra_timestamp=datetime.now().isoformat()
    )


class SecurityMiddleware:
    """보안 미들웨어"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 보안 헤더 추가
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    security_headers = get_security_headers()
                    for key, value in security_headers.items():
                        headers[key.encode()] = value.encode()
                    message["headers"] = list(headers.items())
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


def check_gitignore():
    """Git 보안 확인"""
    import os
    gitignore_path = os.path.join(os.path.dirname(__file__), "..", "..", ".gitignore")

    try:
        with open(gitignore_path, 'r') as f:
            content = f.read()

        required_entries = [".env", "*.env", ".env.local", "*.log"]
        missing_entries = []

        for entry in required_entries:
            if entry not in content:
                missing_entries.append(entry)

        if missing_entries:
            logger.warning(f".gitignore에 누락된 보안 항목들: {missing_entries}")
            return False

        logger.info("✅ .gitignore 보안 검증 완료")
        return True

    except FileNotFoundError:
        logger.warning("⚠️ .gitignore 파일이 없습니다")
        return False


if __name__ == "__main__":
    """보안 모듈 테스트"""
    print("🚀 청년 정책 추천 시스템 - 보안 모듈 테스트")

    # 입력 정화 테스트
    dangerous_input = "<script>alert('xss')</script>test"
    try:
        safe_input = InputSanitizer.sanitize_string(dangerous_input)
        print(f"입력 정화 테스트: '{dangerous_input}' -> '{safe_input}'")
    except SecurityValidationError as e:
        print(f"위험한 입력 차단됨: {e}")

    # 레이트 리미터 테스트
    test_ip = "127.0.0.1"
    for i in range(5):
        allowed = rate_limiter.is_allowed(test_ip, max_requests=3, window_minutes=1)
        print(f"레이트 리미터 테스트 {i+1}: {'허용' if allowed else '차단'}")

    # Git 보안 검사
    check_gitignore()

    print("✅ 보안 모듈 테스트 완료")