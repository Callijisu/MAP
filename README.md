# 청년 정책 추천 시스템

Multi-Agent 협업 기반 청년 맞춤형 정책자금 추천 시스템

## 🚀 빠른 시작

### 1. Python 가상환경 활성화
```bash
# 방법 1: 스크립트 사용
./activate.sh

# 방법 2: 직접 활성화
source venv/bin/activate
```

### 2. 서버 실행
```bash
cd backend
python main.py
```

### 3. API 문서 확인
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Base URL**: http://localhost:8000

## 📁 프로젝트 구조
```
youth-policy-recommender/
├── venv/                    # Python 가상환경
├── backend/
│   ├── agents/             # AI 에이전트
│   ├── api/                # API 엔드포인트
│   ├── core/               # 핵심 로직
│   ├── database/           # 데이터베이스
│   ├── utils/              # 유틸리티
│   ├── tests/              # 테스트
│   └── main.py             # FastAPI 메인 서버
├── frontend/               # 프론트엔드 (예정)
├── data/                   # 데이터 파일
├── docs/                   # 문서
├── scripts/                # 스크립트
├── requirements.txt        # Python 의존성
├── .env.example           # 환경변수 템플릿
└── activate.sh            # 가상환경 활성화 스크립트
```

## 🤖 구현된 Agent

### Agent 1: 사용자 프로필 수집
- **위치**: `backend/agents/agent1_profile.py`
- **기능**: 사용자 기본 정보 수집 및 검증
- **검증 항목**: 나이(15-39), 지역, 소득, 고용상태, 관심분야

## 🔧 환경 설정

### 가상환경 상태
- ✅ Python 3.12.4 가상환경 생성
- ✅ 프로젝트 루트에 `venv/` 폴더
- ✅ 모든 의존성 설치 완료

### 의존성 패키지
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pymongo==4.6.0
- python-dotenv==1.0.0
- openai==1.3.5
- requests==2.31.0
- pydantic==2.5.0

## 🛠 개발 명령어

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 개발모드 실행
cd backend && uvicorn main:app --reload

# Agent 테스트
cd backend && python agents/agent1_profile.py

# 가상환경 비활성화
deactivate
```

## 📡 API 엔드포인트

- `GET /` - 시스템 정보
- `GET /health` - 헬스체크
- `POST /api/profile` - 프로필 생성
- `GET /api/policies` - 정책 목록
- `POST /api/recommend` - 맞춤 추천

## 🔥 다음 단계

- [ ] Stage 3: Agent 2-5 구현
- [ ] MongoDB 연결
- [ ] 실제 정책 데이터 연동
- [ ] 프론트엔드 구현