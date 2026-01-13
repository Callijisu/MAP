# 청년 정책 추천 시스템 - API 문서 📚

Multi-Agent 협업 기반 청년 맞춤형 정책자금 추천 시스템의 완전한 API 명세서입니다.

## 📋 목차

- [기본 정보](#기본-정보)
- [인증 및 보안](#인증-및-보안)
- [시스템 정보 API](#시스템-정보-api)
- [프로필 관리 API](#프로필-관리-api)
- [정책 조회 API](#정책-조회-api)
- [추천 시스템 API](#추천-시스템-api)
- [사용자 이력 API](#사용자-이력-api)
- [에러 코드](#에러-코드)
- [사용 예시](#사용-예시)

## 🌐 기본 정보

**Base URL**: `http://localhost:8000`

**API Version**: `v1.0.0`

**Content-Type**: `application/json`

**Interactive Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔒 인증 및 보안

현재 버전에서는 API 키 인증이 필요하지 않으며, 모든 엔드포인트가 공개되어 있습니다.

### 보안 고려사항
- Rate Limiting: 분당 100회 요청 제한
- Input Validation: 모든 입력 데이터 검증
- CORS 설정: 허용된 오리진만 접근 가능

## 📊 시스템 정보 API

### 1. 시스템 정보 조회

**Endpoint**: `GET /`

**Description**: 시스템의 기본 정보와 사용 가능한 엔드포인트를 반환합니다.

**Request**:
```bash
curl http://localhost:8000/
```

**Response**:
```json
{
  "service": "청년 정책 추천 시스템",
  "version": "1.0.0",
  "description": "Multi-Agent 협업 기반 청년 맞춤형 정책자금 추천 시스템",
  "status": "running",
  "database_connected": true,
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "profile": "/api/profile",
    "policies": "/api/policies",
    "recommend": "/api/recommend",
    "match": "/api/match",
    "explain": "/api/explain",
    "orchestrator": "/api/orchestrator"
  }
}
```

### 2. 헬스 체크

**Endpoint**: `GET /health`

**Description**: 시스템과 데이터베이스의 연결 상태를 확인합니다.

**Request**:
```bash
curl http://localhost:8000/health
```

**Response (정상)**:
```json
{
  "status": "healthy",
  "database": "connected",
  "database_info": {
    "name": "youth_policy",
    "collections": 3,
    "size_mb": 2.5
  },
  "timestamp": "2026-01-09T10:30:00Z"
}
```

**Response (DB 연결 실패)**:
```json
{
  "status": "healthy",
  "database": "disconnected",
  "timestamp": "2026-01-09T10:30:00Z"
}
```

## 👤 프로필 관리 API

### 3. 프로필 생성

**Endpoint**: `POST /api/profile`

**Description**: 사용자의 기본 정보를 받아 프로필을 생성하고 데이터베이스에 저장합니다.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "interest": "창업"
  }'
```

**Request Body**:
| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| age | integer | ✅ | 나이 (18-39세) | 28 |
| region | string | ✅ | 거주 지역 | "서울" |
| income | integer | ✅ | 연소득 (만원 단위) | 3000 |
| employment | string | ✅ | 고용 상태 | "재직자", "구직자", "자영업" |
| interest | string | ❌ | 관심 분야 | "창업", "부동산", "문화" |

**Response (성공)**:
```json
{
  "success": true,
  "profile_id": "profile_1705302600_abc123",
  "message": "프로필이 성공적으로 생성되었습니다. (데이터베이스 저장 완료)"
}
```

**Error Responses**:
- `400`: 잘못된 요청 데이터
- `500`: 서버 오류

### 4. 프로필 조회

**Endpoint**: `GET /api/profile/{profile_id}`

**Description**: 저장된 프로필 정보를 조회합니다.

**Request**:
```bash
curl http://localhost:8000/api/profile/profile_1705302600_abc123
```

**Response (성공)**:
```json
{
  "success": true,
  "profile": {
    "profile_id": "profile_1705302600_abc123",
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "interest": "창업",
    "created_at": "2026-01-09T10:30:00.123456Z"
  },
  "message": "프로필 조회 완료"
}
```

### 5. 프로필 수정

**Endpoint**: `PUT /api/profile/{user_id}`

**Description**: 기존 프로필 정보를 업데이트합니다.

**Request**:
```bash
curl -X PUT "http://localhost:8000/api/profile/profile_1705302600_abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 29,
    "region": "서울",
    "income": 3500,
    "employment": "재직자",
    "interest": "부동산"
  }'
```

**Response (성공)**:
```json
{
  "success": true,
  "profile_id": "profile_1705302600_abc123",
  "message": "프로필이 성공적으로 업데이트되었습니다."
}
```

## 📋 정책 조회 API

### 6. 정책 목록 조회

**Endpoint**: `GET /api/policies`

**Description**: 필터링 옵션과 함께 정책 목록을 조회합니다.

**Request**:
```bash
curl "http://localhost:8000/api/policies?category=창업&region=서울&page=1&limit=10"
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|----------|------|------|------|------|
| category | string | ❌ | 정책 카테고리 | "창업", "주거", "일자리", "금융" |
| region | string | ❌ | 대상 지역 | "서울", "경기", "전국" |
| page | integer | ❌ | 페이지 번호 (기본값: 1) | 1, 2, 3... |
| limit | integer | ❌ | 페이지당 결과 수 (기본값: 20, 최대: 100) | 10, 20, 50 |

**Response (성공)**:
```json
[
  {
    "id": "JOB_001",
    "title": "청년 창업 지원금",
    "description": "만 18~39세 청년 창업자 대상 최대 5천만원 지원",
    "category": "창업"
  },
  {
    "id": "FIN_001",
    "title": "청년희망적금",
    "description": "월 10만원 적립시 정부지원금 10만원",
    "category": "금융"
  }
]
```

### 7. 정책 상세 조회

**Endpoint**: `GET /api/policy/{policy_id}`

**Description**: 특정 정책의 상세 정보를 조회합니다.

**Request**:
```bash
curl http://localhost:8000/api/policy/JOB_001
```

**Response (성공)**:
```json
{
  "success": true,
  "policy": {
    "id": "JOB_001",
    "title": "청년 창업 지원금",
    "description": "최대 5천만원 지원",
    "category": "창업",
    "target_age": "18-39세",
    "target_region": ["전국"],
    "target_employment": ["구직자", "자영업"],
    "budget_max": 5000,
    "deadline": "2024년 12월 31일",
    "application_url": "https://startup.go.kr"
  },
  "message": "정책 상세 조회 완료"
}
```

## 🎯 추천 시스템 API

### 8. 통합 정책 추천 (권장)

**Endpoint**: `POST /api/orchestrator`

**Description**: 모든 Agent를 통합하여 개인화된 정책 추천을 제공합니다. **가장 권장되는 API**입니다.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/orchestrator" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "interest": "창업",
    "min_score": 40.0,
    "max_results": 5
  }'
```

**Request Body**:
| 필드 | 타입 | 필수 | 설명 | 기본값 |
|------|------|------|------|--------|
| age | integer | ✅ | 나이 (18-39세) | - |
| region | string | ✅ | 거주 지역 | - |
| income | integer | ✅ | 연소득 (만원) | - |
| employment | string | ✅ | 고용 상태 | - |
| interest | string | ❌ | 관심 분야 | null |
| min_score | float | ❌ | 최소 매칭 점수 | 40.0 |
| max_results | integer | ❌ | 최대 결과 수 | 10 |

**Response (성공)**:
```json
{
  "session_id": "session_1705302600_xyz789",
  "success": true,
  "message": "5개의 정책을 성공적으로 추천했습니다.",
  "processing_time": 0.002,
  "steps_summary": [
    {
      "agent": "Agent1 (Profile)",
      "status": "success",
      "duration": 0.00,
      "result": "프로필 검증 및 저장 완료"
    },
    {
      "agent": "Agent2 (Data)",
      "status": "success",
      "duration": 0.00,
      "result": "정책 데이터 조회 완료"
    },
    {
      "agent": "Agent3 (Matching)",
      "status": "success",
      "duration": 0.00,
      "result": "매칭 및 점수 계산 완료"
    },
    {
      "agent": "Agent4 (GPT)",
      "status": "success",
      "duration": 0.00,
      "result": "GPT 설명 생성 완료"
    },
    {
      "agent": "Agent5 (Presentation)",
      "status": "success",
      "duration": 0.00,
      "result": "결과 포맷팅 완료"
    }
  ],
  "recommendation_result": {
    "user_profile_summary": "28세, 서울 거주, 연소득 3,000만원, 재직자, 관심분야: 창업",
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
        "match_reasons": [
          "연령 조건 만족 (18-39세)",
          "창업 관심도 일치",
          "소득 조건 적합"
        ],
        "benefit_summary": "최대 5천만원 창업 자금 지원",
        "deadline": "2024년 12월 31일",
        "explanation": "회원님의 창업 관심도와 현재 소득 수준을 고려할 때 가장 적합한 정책입니다...",
        "explanation_meta": {
          "gpt_model": "fallback",
          "tokens_used": 0,
          "generation_time": "0.00s"
        }
      }
    ]
  },
  "generated_at": "2026-01-09T10:30:00.123456Z"
}
```

### 9. 정책 매칭

**Endpoint**: `POST /api/match`

**Description**: Agent2와 Agent3를 사용하여 정책 매칭만 수행합니다.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/match" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "min_score": 40.0,
    "max_results": 10
  }'
```

**Response (성공)**:
```json
{
  "success": true,
  "message": "매칭이 완료되었습니다.",
  "user_profile_summary": "28세, 서울 거주, 연소득 3,000만원, 재직자",
  "total_matches": 3,
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
      "match_reasons": [
        "연령 조건 만족",
        "지역 조건 적합"
      ],
      "benefit_summary": "최대 5천만원 지원",
      "deadline": "2024년 12월 31일"
    }
  ]
}
```

### 10. 정책 설명 생성

**Endpoint**: `POST /api/explain`

**Description**: Agent4(GPT-4)를 사용하여 개인 맞춤형 정책 설명을 생성합니다.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "interest": "창업",
    "policies": [
      {
        "policy_id": "JOB_001",
        "title": "청년 창업 지원금",
        "category": "창업",
        "score": 89.5,
        "match_reasons": ["연령 조건 만족", "창업 관심도 일치"],
        "benefit_summary": "최대 5천만원 지원",
        "deadline": "2024년 12월 31일"
      }
    ]
  }'
```

**Response (성공)**:
```json
{
  "success": true,
  "message": "1개 정책에 대한 설명이 생성되었습니다.",
  "user_profile_summary": "28세, 서울 거주, 연소득 3,000만원, 재직자, 관심분야: 창업",
  "total_explained": 1,
  "policies": [
    {
      "policy_id": "JOB_001",
      "title": "청년 창업 지원금",
      "category": "창업",
      "score": 89.5,
      "match_reasons": ["연령 조건 만족", "창업 관심도 일치"],
      "benefit_summary": "최대 5천만원 지원",
      "deadline": "2024년 12월 31일",
      "explanation": "회원님의 창업 관심사와 현재 재직 상태를 고려할 때, 이 정책은 안정적인 창업 준비를 위한 최적의 선택입니다...",
      "explanation_meta": {
        "gpt_model": "fallback",
        "tokens_used": 0,
        "generation_time": "0.00s"
      }
    }
  ]
}
```

### 11. 레거시 추천

**Endpoint**: `POST /api/recommend`

**Description**: 기존 시스템과의 호환성을 위한 단순 추천 API입니다.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "profile_1705302600_abc123"
  }'
```

**Response**:
```json
{
  "success": true,
  "profile_id": "profile_1705302600_abc123",
  "recommendations": [
    {
      "id": "rec_001",
      "title": "맞춤형 청년 창업 지원",
      "description": "회원님의 프로필에 맞는 창업 지원 프로그램",
      "category": "창업"
    }
  ],
  "message": "맞춤형 정책 추천이 완료되었습니다. (레거시 버전)"
}
```

## 📈 사용자 이력 API

### 12. 추천 이력 조회

**Endpoint**: `GET /api/user/{user_id}/history`

**Description**: 사용자의 정책 추천 이력을 조회합니다.

**Request**:
```bash
curl http://localhost:8000/api/user/profile_1705302600_abc123/history
```

**Response (성공)**:
```json
{
  "success": true,
  "user_id": "profile_1705302600_abc123",
  "history": [
    {
      "date": "2026-01-09T10:30:00Z",
      "session_id": "session_1705302600_xyz789",
      "recommended_policies": 3,
      "avg_score": 85.7,
      "top_category": "창업"
    }
  ],
  "total_sessions": 1,
  "message": "1개의 추천 이력을 찾았습니다."
}
```

## ❌ 에러 코드

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 400 | Bad Request | 잘못된 요청 데이터 |
| 404 | Not Found | 요청한 리소스를 찾을 수 없음 |
| 422 | Unprocessable Entity | 입력 데이터 검증 실패 |
| 500 | Internal Server Error | 서버 내부 오류 |
| 503 | Service Unavailable | 데이터베이스 연결 불가 |

### 공통 에러 응답 형식

```json
{
  "detail": "오류 메시지",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2026-01-09T10:30:00Z"
}
```

### 주요 에러 시나리오

1. **프로필 생성 오류**
   - 나이 범위 초과 (18-39세 외)
   - 필수 필드 누락
   - 음수 소득 입력

2. **정책 조회 오류**
   - 존재하지 않는 정책 ID
   - 잘못된 페이지 번호

3. **추천 시스템 오류**
   - OpenAI API 키 미설정 (Fallback 모드 전환)
   - MongoDB 연결 실패 (로컬 모드 전환)

## 📖 사용 예시

### cURL 예시

```bash
# 1. 시스템 상태 확인
curl http://localhost:8000/health

# 2. 프로필 생성
curl -X POST http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "interest": "창업"
  }'

# 3. 통합 추천 (권장)
curl -X POST http://localhost:8000/api/orchestrator \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "interest": "창업",
    "min_score": 40.0,
    "max_results": 5
  }'
```

### Python 예시

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 프로필 생성
profile_data = {
    "age": 28,
    "region": "서울",
    "income": 3000,
    "employment": "재직자",
    "interest": "창업"
}

response = requests.post(f"{BASE_URL}/api/profile", json=profile_data)
profile_result = response.json()
print(f"프로필 ID: {profile_result['profile_id']}")

# 2. 통합 추천
recommend_data = profile_data.copy()
recommend_data.update({
    "min_score": 40.0,
    "max_results": 5
})

response = requests.post(f"{BASE_URL}/api/orchestrator", json=recommend_data)
recommendation = response.json()

print(f"추천 정책 수: {recommendation['recommendation_result']['total_recommendations']}")
for policy in recommendation['recommendation_result']['recommendations']:
    print(f"- {policy['title']} (점수: {policy['score']})")
```

### JavaScript (fetch) 예시

```javascript
// 통합 추천 요청
async function getRecommendations() {
  const profileData = {
    age: 28,
    region: "서울",
    income: 3000,
    employment: "재직자",
    interest: "창업",
    min_score: 40.0,
    max_results: 5
  };

  try {
    const response = await fetch('http://localhost:8000/api/orchestrator', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData)
    });

    const result = await response.json();

    if (result.success) {
      console.log(`추천 완료: ${result.recommendation_result.total_recommendations}개 정책`);
      result.recommendation_result.recommendations.forEach(policy => {
        console.log(`- ${policy.title} (${policy.score}점)`);
      });
    }
  } catch (error) {
    console.error('추천 요청 실패:', error);
  }
}

getRecommendations();
```

## 🔧 추가 정보

### 성능 최적화

- **응답 시간**: 대부분의 API는 0.01초 이내 응답
- **통합 추천**: 목표 5초 이내 (현재 평균 0.002초)
- **캐싱**: 정책 데이터 및 프로필 정보 캐싱 적용

### 개발 팁

1. **Interactive Documentation 활용**: `/docs` 엔드포인트에서 API를 직접 테스트할 수 있습니다.

2. **에러 처리**: 모든 요청에 대해 적절한 에러 처리를 구현하세요.

3. **Rate Limiting**: 프로덕션 환경에서는 Rate Limiting을 고려하세요.

4. **로컬 개발**: MongoDB 연결이 실패해도 Fallback 모드로 동작합니다.

---

**문서 버전**: 1.0.0
**마지막 업데이트**: 2026년 1월 9일
**문의**: contact@youth-policy.kr