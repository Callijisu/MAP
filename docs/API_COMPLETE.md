# 청년 정책 추천 시스템 - API 문서 📚

Multi-Agent 협업 기반 청년 맞춤형 정책자금 추천 시스템의 완전한 API 명세서입니다.

## 📋 목차

- [기본 정보](#기본-정보)
- [시스템 정보 API](#시스템-정보-api)
- [프로필 관리 API](#프로필-관리-api)
- [정책 조회 API](#정책-조회-api)
- [추천 시스템 API](#추천-시스템-api)
- [사용자 이력 API](#사용자-이력-api)
- [에러 코드](#에러-코드)

## 🌐 기본 정보

**Base URL**: `http://localhost:8000`
**API Version**: `v1.0.0`
**Content-Type**: `application/json`

**Interactive Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 시스템 정보 API

### 1. 시스템 정보 조회
**Endpoint**: `GET /`
**Description**: 시스템의 기본 정보와 사용 가능한 엔드포인트를 반환합니다.

```bash
curl http://localhost:8000/
```

**Response**:
```json
{
  "service": "청년 정책 추천 시스템",
  "version": "1.0.0",
  "status": "running",
  "database_connected": true,
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "profile": "/api/profile",
    "policies": "/api/policies",
    "orchestrator": "/api/orchestrator"
  }
}
```

### 2. 헬스 체크
**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

## 👤 프로필 관리 API

### 3. 프로필 생성
**Endpoint**: `POST /api/profile`

**Request Body**:
```json
{
  "age": 28,
  "region": "서울",
  "income": 3000,
  "employment": "재직자",
  "interest": "창업"
}
```

**Response**:
```json
{
  "success": true,
  "profile_id": "profile_123456789",
  "message": "프로필이 성공적으로 생성되었습니다."
}
```

### 4. 프로필 조회
**Endpoint**: `GET /api/profile/{profile_id}`

### 5. 프로필 수정
**Endpoint**: `PUT /api/profile/{user_id}`

## 📋 정책 조회 API

### 6. 정책 목록 조회
**Endpoint**: `GET /api/policies`

**Query Parameters**:
- `category` (string, optional): 정책 카테고리
- `page` (integer, optional): 페이지 번호 (기본값: 1)
- `limit` (integer, optional): 페이지당 결과 수 (기본값: 20)

**Response**:
```json
[
  {
    "id": "policy_001",
    "title": "청년 창업 지원금",
    "description": "만 18~39세 청년 창업자 대상 최대 5천만원 지원",
    "category": "창업"
  }
]
```

### 7. 정책 상세 조회
**Endpoint**: `GET /api/policy/{policy_id}`

## 🎯 추천 시스템 API

### 8. 통합 추천 (권장)
**Endpoint**: `POST /api/orchestrator`

**Description**: 모든 Agent를 통합하여 개인화된 정책 추천을 제공합니다.

**Request Body**:
```json
{
  "age": 28,
  "region": "서울",
  "income": 3000,
  "employment": "재직자",
  "interest": "창업",
  "min_score": 40.0,
  "max_results": 5
}
```

**Response**:
```json
{
  "session_id": "session_123456789",
  "success": true,
  "message": "통합 추천이 완료되었습니다.",
  "processing_time": 0.002,
  "steps_summary": [
    {
      "agent": "Agent1_Profile",
      "status": "success",
      "processing_time": 0.00,
      "message": "프로필 수집 및 검증 완료"
    }
  ],
  "recommendation_result": {
    "user_profile_summary": "28세, 서울 거주, 연소득 3,000만원, 재직자",
    "total_recommendations": 3,
    "avg_score": 85.7,
    "category_distribution": {
      "창업": 2,
      "금융": 1
    },
    "recommendations": [
      {
        "policy_id": "JOB_001",
        "title": "청년 창업 지원금",
        "category": "창업",
        "score": 89.5,
        "match_reasons": ["연령 조건 만족", "창업 관심도 일치"],
        "benefit_summary": "최대 5천만원 지원",
        "explanation": "회원님의 창업 관심사와 현재 재직 상태를 고려할 때..."
      }
    ]
  }
}
```

### 9. 정책 매칭
**Endpoint**: `POST /api/match`

**Description**: Agent2와 Agent3가 협업하여 정책 매칭을 수행합니다.

### 10. 정책 설명 생성
**Endpoint**: `POST /api/explain`

**Description**: Agent4(GPT-4)를 사용하여 정책에 대한 개인화된 설명을 생성합니다.

## 📈 사용자 이력 API

### 11. 추천 이력 조회
**Endpoint**: `GET /api/user/{user_id}/history`

## ❌ 에러 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 400 | Bad Request | 잘못된 요청 데이터 |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 422 | Unprocessable Entity | 입력 데이터 검증 실패 |
| 500 | Internal Server Error | 서버 내부 오류 |

### 일반적인 에러 응답
```json
{
  "detail": "에러 메시지 설명"
}
```

## 📖 사용 예시

### cURL 예시
```bash
# 1. 프로필 생성
curl -X POST http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -d '{"age": 28, "region": "서울", "income": 3000, "employment": "재직자", "interest": "창업"}'

# 2. 통합 추천
curl -X POST http://localhost:8000/api/orchestrator \
  -H "Content-Type: application/json" \
  -d '{"age": 28, "region": "서울", "income": 3000, "employment": "재직자", "interest": "창업", "min_score": 40.0, "max_results": 5}'
```

### Python 예시
```python
import requests

# 통합 추천 요청
response = requests.post('http://localhost:8000/api/orchestrator', json={
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "interest": "창업",
    "min_score": 40.0,
    "max_results": 5
})

result = response.json()
print(f"추천 정책 수: {result['recommendation_result']['total_recommendations']}")
```

---

**API 버전**: v1.0.0
**최종 업데이트**: 2026년 1월 9일
**문의**: contact@youth-policy.kr