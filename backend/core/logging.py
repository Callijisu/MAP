"""
청년 정책 추천 시스템 - 구조화된 로깅 시스템
파일 및 콘솔 출력을 지원하는 통합 로깅 관리
"""

import logging
import logging.handlers
import sys
import json
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Union
from pathlib import Path
import functools

from .config import get_settings


class ColorFormatter(logging.Formatter):
    """컬러 출력을 위한 로그 포매터"""

    # ANSI 컬러 코드
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """컬러가 적용된 로그 메시지 포매팅"""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"

        # 로그 메시지에 이모지 추가
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        emoji = emoji_map.get(record.levelname.strip('\033[0m\033[31m\033[32m\033[33m\033[35m\033[36m'), '📝')
        record.msg = f"{emoji} {record.msg}"

        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON 형태로 로그를 포매팅"""

    def format(self, record):
        """로그 레코드를 JSON으로 변환"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # 예외 정보 추가
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # 추가 필드 포함
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry, ensure_ascii=False, indent=None)


class StructuredLogger:
    """구조화된 로깅을 위한 래퍼 클래스"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """로거 초기 설정"""
        if not self.logger.handlers:
            settings = get_settings()

            # 로그 레벨 설정
            self.logger.setLevel(getattr(logging, settings.log_level))

            # 콘솔 핸들러 추가
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, settings.log_level))
            console_handler.setFormatter(ColorFormatter(settings.log_format))
            self.logger.addHandler(console_handler)

            # 파일 핸들러 추가 (설정된 경우)
            if settings.log_file:
                self._add_file_handler(settings)

            # 중복 로그 방지
            self.logger.propagate = False

    def _add_file_handler(self, settings):
        """파일 핸들러 추가"""
        try:
            # 로그 디렉토리 생성
            log_file_path = Path(settings.log_file)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # 회전 파일 핸들러 (크기 기반)
            file_handler = logging.handlers.RotatingFileHandler(
                filename=settings.log_file,
                maxBytes=settings.log_max_bytes,
                backupCount=settings.log_backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)  # 파일에는 모든 로그 저장
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)

        except Exception as e:
            self.logger.error(f"파일 핸들러 설정 실패: {e}")

    def _log_with_context(self, level: str, message: str, **kwargs):
        """컨텍스트 정보와 함께 로깅"""
        extra_fields = {}

        # 추가 필드 처리
        for key, value in kwargs.items():
            if key.startswith('extra_'):
                extra_fields[key[6:]] = value  # 'extra_' 제거
            else:
                extra_fields[key] = value

        # 로그 레코드에 추가 정보 포함
        getattr(self.logger, level.lower())(
            message,
            extra={'extra_fields': extra_fields}
        )

    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        self._log_with_context('DEBUG', message, **kwargs)

    def info(self, message: str, **kwargs):
        """정보 로그"""
        self._log_with_context('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """경고 로그"""
        self._log_with_context('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """에러 로그"""
        self._log_with_context('ERROR', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """심각한 에러 로그"""
        self._log_with_context('CRITICAL', message, **kwargs)

    def exception(self, message: str, **kwargs):
        """예외 정보와 함께 로그"""
        self.logger.exception(message, extra={'extra_fields': kwargs})


class AgentLogger(StructuredLogger):
    """Agent 전용 로거"""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(f"agent.{agent_name}")

    def log_agent_start(self, operation: str, **context):
        """Agent 작업 시작 로깅"""
        self.info(
            f"{self.agent_name} 작업 시작: {operation}",
            extra_operation=operation,
            extra_agent=self.agent_name,
            **context
        )

    def log_agent_success(self, operation: str, duration: float, **context):
        """Agent 작업 성공 로깅"""
        self.info(
            f"{self.agent_name} 작업 완료: {operation} ({duration:.3f}초)",
            extra_operation=operation,
            extra_agent=self.agent_name,
            extra_duration=duration,
            **context
        )

    def log_agent_error(self, operation: str, error: Exception, **context):
        """Agent 작업 실패 로깅"""
        self.error(
            f"{self.agent_name} 작업 실패: {operation} - {str(error)}",
            extra_operation=operation,
            extra_agent=self.agent_name,
            extra_error_type=type(error).__name__,
            extra_error_message=str(error),
            **context
        )

    def log_agent_warning(self, operation: str, warning_message: str, **context):
        """Agent 경고 로깅"""
        self.warning(
            f"{self.agent_name} 경고: {operation} - {warning_message}",
            extra_operation=operation,
            extra_agent=self.agent_name,
            extra_warning=warning_message,
            **context
        )


class APILogger(StructuredLogger):
    """API 요청/응답 전용 로거"""

    def __init__(self):
        super().__init__("api")

    def log_request(self, method: str, path: str, client_ip: str, **context):
        """API 요청 로깅"""
        self.info(
            f"API 요청: {method} {path}",
            extra_method=method,
            extra_path=path,
            extra_client_ip=client_ip,
            **context
        )

    def log_response(self, method: str, path: str, status_code: int, duration: float, **context):
        """API 응답 로깅"""
        level = "info" if status_code < 400 else "error"
        getattr(self, level)(
            f"API 응답: {method} {path} - {status_code} ({duration:.3f}초)",
            extra_method=method,
            extra_path=path,
            extra_status_code=status_code,
            extra_duration=duration,
            **context
        )

    def log_api_error(self, method: str, path: str, error: Exception, **context):
        """API 에러 로깅"""
        self.error(
            f"API 에러: {method} {path} - {str(error)}",
            extra_method=method,
            extra_path=path,
            extra_error_type=type(error).__name__,
            extra_error_message=str(error),
            **context
        )


class DatabaseLogger(StructuredLogger):
    """데이터베이스 전용 로거"""

    def __init__(self):
        super().__init__("database")

    def log_connection(self, database_name: str, status: str, **context):
        """데이터베이스 연결 로깅"""
        level = "info" if status == "success" else "error"
        getattr(self, level)(
            f"데이터베이스 연결 {status}: {database_name}",
            extra_database=database_name,
            extra_status=status,
            **context
        )

    def log_query(self, collection: str, operation: str, duration: float, **context):
        """데이터베이스 쿼리 로깅"""
        self.debug(
            f"DB 쿼리: {collection}.{operation} ({duration:.3f}초)",
            extra_collection=collection,
            extra_operation=operation,
            extra_duration=duration,
            **context
        )

    def log_query_error(self, collection: str, operation: str, error: Exception, **context):
        """데이터베이스 쿼리 에러 로깅"""
        self.error(
            f"DB 쿼리 실패: {collection}.{operation} - {str(error)}",
            extra_collection=collection,
            extra_operation=operation,
            extra_error_type=type(error).__name__,
            extra_error_message=str(error),
            **context
        )


def get_logger(name: str) -> StructuredLogger:
    """일반 로거 생성"""
    return StructuredLogger(name)


def get_agent_logger(agent_name: str) -> AgentLogger:
    """Agent 로거 생성"""
    return AgentLogger(agent_name)


def get_api_logger() -> APILogger:
    """API 로거 생성"""
    return APILogger()


def get_database_logger() -> DatabaseLogger:
    """데이터베이스 로거 생성"""
    return DatabaseLogger()


# 로깅 데코레이터
def log_execution_time(logger: Optional[StructuredLogger] = None):
    """함수 실행 시간을 로깅하는 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)

            start_time = datetime.now()
            try:
                logger.debug(f"함수 실행 시작: {func.__name__}")
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(
                    f"함수 실행 완료: {func.__name__} ({duration:.3f}초)",
                    extra_function=func.__name__,
                    extra_duration=duration
                )
                return result
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.error(
                    f"함수 실행 실패: {func.__name__} ({duration:.3f}초) - {str(e)}",
                    extra_function=func.__name__,
                    extra_duration=duration,
                    extra_error=str(e)
                )
                raise
        return wrapper
    return decorator


def log_agent_operation(agent_name: str):
    """Agent 작업을 로깅하는 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_agent_logger(agent_name)
            operation = func.__name__

            start_time = datetime.now()
            try:
                logger.log_agent_start(operation)
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.log_agent_success(operation, duration)
                return result
            except Exception as e:
                logger.log_agent_error(operation, e)
                raise
        return wrapper
    return decorator


# 로그 레벨 동적 변경
class LogLevelManager:
    """로그 레벨 동적 관리"""

    @staticmethod
    def set_log_level(level: str):
        """전체 로그 레벨 변경"""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger().setLevel(numeric_level)

        # 모든 핸들러의 레벨도 변경
        for handler in logging.getLogger().handlers:
            handler.setLevel(numeric_level)

    @staticmethod
    def set_logger_level(logger_name: str, level: str):
        """특정 로거의 레벨 변경"""
        logger = logging.getLogger(logger_name)
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)

    @staticmethod
    def get_logger_levels() -> Dict[str, str]:
        """현재 로거들의 레벨 반환"""
        loggers = {}
        for name in logging.getLogger().manager.loggerDict.keys():
            logger = logging.getLogger(name)
            loggers[name] = logging.getLevelName(logger.level)
        return loggers


# 로깅 시스템 초기화
def setup_logging():
    """로깅 시스템 초기화"""
    try:
        settings = get_settings()

        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.log_level))

        # 기존 핸들러 제거
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        print("✅ 로깅 시스템 초기화 완료")

    except Exception as e:
        print(f"❌ 로깅 시스템 초기화 실패: {e}")


def log_system_info():
    """시스템 정보 로깅"""
    logger = get_logger("system")
    settings = get_settings()

    logger.info(
        "시스템 시작",
        extra_app_name=settings.app_name,
        extra_version=settings.app_version,
        extra_environment=settings.environment,
        extra_debug_mode=settings.debug
    )


if __name__ == "__main__":
    """로깅 모듈 테스트"""
    print("🚀 청년 정책 추천 시스템 - 로깅 시스템 테스트")

    # 로깅 시스템 초기화
    setup_logging()

    # 각종 로거 테스트
    general_logger = get_logger("test")
    agent_logger = get_agent_logger("test_agent")
    api_logger = get_api_logger()
    db_logger = get_database_logger()

    # 로그 레벨별 테스트
    general_logger.debug("디버그 메시지 테스트")
    general_logger.info("정보 메시지 테스트")
    general_logger.warning("경고 메시지 테스트")
    general_logger.error("에러 메시지 테스트")

    # Agent 로그 테스트
    agent_logger.log_agent_start("test_operation")
    agent_logger.log_agent_success("test_operation", 0.123)

    # API 로그 테스트
    api_logger.log_request("GET", "/test", "127.0.0.1")
    api_logger.log_response("GET", "/test", 200, 0.045)

    # DB 로그 테스트
    db_logger.log_connection("test_db", "success")
    db_logger.log_query("test_collection", "find", 0.012)

    print("✅ 로깅 시스템 테스트 완료")