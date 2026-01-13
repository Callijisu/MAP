# 청년 정책 추천 시스템 - 배포 준비 체크리스트 ✅

**Stage 10 - 최종 배포 준비 가이드**

---

## 📋 배포 전 필수 체크리스트

### 🔒 **보안 설정** (Critical - 반드시 완료)

- [ ] **MongoDB 자격증명 보안 처리**
  ```bash
  # 1. MongoDB Atlas에서 비밀번호 변경
  # 2. .env 파일에서 실제 자격증명 제거
  # 3. 환경변수로 관리 설정
  ```

- [ ] **OpenAI API 키 설정**
  ```bash
  # .env 파일에 실제 API 키 추가
  OPENAI_API_KEY=sk-your-actual-api-key-here
  ```

- [ ] **.env 파일 Git 제외 확인**
  ```bash
  # .gitignore에 다음이 포함되어야 함:
  .env
  *.env
  !.env.example
  ```

- [ ] **프로덕션 환경 변수 설정**
  ```bash
  export DEBUG=False
  export LOG_LEVEL=WARNING
  export ENVIRONMENT=production
  ```

### 🏗️ **시스템 환경 준비**

- [ ] **Python 환경 설정**
  ```bash
  # Python 3.12 이상 설치 확인
  python --version  # 3.12+

  # 가상환경 생성 및 활성화
  python -m venv venv
  source venv/bin/activate  # Linux/macOS
  # venv\Scripts\activate    # Windows
  ```

- [ ] **의존성 설치**
  ```bash
  cd backend
  pip install -r requirements.txt

  # 필수 패키지 확인
  pip list | grep -E "(fastapi|pydantic|pymongo|openai)"
  ```

- [ ] **MongoDB 연결 테스트**
  ```bash
  # 연결 확인
  python -c "
  from database.mongo_handler import get_mongodb_handler
  handler = get_mongodb_handler()
  status = handler.test_connection()
  print('DB 연결:', status.get('connected', False))
  "
  ```

### 🧪 **기능 테스트**

- [ ] **서버 시작 테스트**
  ```bash
  # 개발 모드 테스트
  uvicorn main:app --reload --port 8000

  # 프로덕션 모드 테스트
  uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
  ```

- [ ] **API 엔드포인트 테스트**
  ```bash
  # 헬스 체크
  curl http://localhost:8000/health

  # 프로필 생성 테스트
  curl -X POST http://localhost:8000/api/profile \
    -H "Content-Type: application/json" \
    -d '{"age":28,"region":"서울","income":3000,"employment":"재직자","interest":"창업"}'

  # 통합 추천 테스트
  curl -X POST http://localhost:8000/api/orchestrator \
    -H "Content-Type: application/json" \
    -d '{"age":28,"region":"서울","income":3000,"employment":"재직자","interest":"창업","min_score":40.0,"max_results":5}'
  ```

- [ ] **종합 테스트 실행**
  ```bash
  # 자동화된 시스템 테스트 실행
  python test_system.py

  # 예상 결과: 모든 테스트 통과 (성공률 90% 이상)
  ```

### 📊 **성능 및 모니터링**

- [ ] **응답 시간 확인**
  ```bash
  # API 응답 시간 측정 (5초 이내 목표)
  time curl -X POST http://localhost:8000/api/orchestrator \
    -H "Content-Type: application/json" \
    -d '{"age":28,"region":"서울","income":3000,"employment":"재직자"}'
  ```

- [ ] **메모리 사용량 확인**
  ```bash
  # 서버 실행 후 메모리 사용량 체크
  ps aux | grep uvicorn
  ```

- [ ] **로그 시스템 확인**
  ```bash
  # 로그가 정상적으로 출력되는지 확인
  # 콘솔에 다음과 같은 로그가 표시되어야 함:
  # ✅ 로깅 시스템 초기화 완료
  # ✅ 시스템 시작
  ```

### 📁 **파일 및 구조 정리**

- [ ] **불필요한 파일 제거**
  ```bash
  # 캐시 파일 정리
  find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
  find . -name "*.pyc" -delete 2>/dev/null

  # 로그 파일 정리
  rm -f *.log
  ```

- [ ] **프로젝트 구조 확인**
  ```
  youth-policy-recommender/
  ├── backend/
  │   ├── agents/          # 5개 Agent 파일 존재 확인
  │   ├── core/            # 4개 core 모듈 확인
  │   ├── database/        # MongoDB 관련 파일
  │   ├── docs/            # API 문서
  │   ├── tests/           # 테스트 파일
  │   ├── main.py          # FastAPI 서버
  │   ├── orchestrator.py  # Agent 통합 관리자
  │   └── requirements.txt # 의존성 목록
  ├── docs/                # 프로젝트 문서
  └── README.md            # 프로젝트 설명
  ```

### 📚 **문서화 완성도**

- [ ] **README.md 확인**
  - [ ] 설치 가이드 완성
  - [ ] 사용법 설명 포함
  - [ ] API 엔드포인트 목록
  - [ ] 시스템 요구사항

- [ ] **API 문서 확인**
  - [ ] docs/API.md 완성 (720+ 줄)
  - [ ] Swagger UI 접근 가능 (http://localhost:8000/docs)
  - [ ] 모든 엔드포인트 문서화

---

## 🚀 배포 단계별 가이드

### **1단계: 로컬 테스트 (개발 환경)**

```bash
# 1. 의존성 설치
cd backend
pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
nano .env  # MongoDB URI, OpenAI API Key 설정

# 3. 서버 시작
uvicorn main:app --reload

# 4. 테스트 실행
python test_system.py
```

**예상 결과**: ✅ 모든 Agent 작동, API 응답 시간 < 1초

### **2단계: 스테이징 환경 배포**

```bash
# 1. 프로덕션 설정
export DEBUG=False
export LOG_LEVEL=WARNING

# 2. 서버 시작 (단일 워커)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1

# 3. 부하 테스트
# 동시 요청 10개 테스트
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/orchestrator \
    -H "Content-Type: application/json" \
    -d '{"age":28,"region":"서울","income":3000,"employment":"재직자"}' &
done
wait
```

**예상 결과**: ✅ 동시 요청 처리 성공, 메모리 사용량 < 500MB

### **3단계: 프로덕션 배포**

```bash
# 1. 최적화된 설정
export WORKERS=4  # CPU 코어 수에 따라 조정
export PORT=8000

# 2. 프로덕션 서버 시작
uvicorn main:app --host 0.0.0.0 --port $PORT --workers $WORKERS

# 또는 Gunicorn 사용 (권장)
pip install gunicorn
gunicorn main:app -w $WORKERS -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**예상 결과**: ✅ 안정적인 서비스 운영, 고가용성 확보

---

## 🔧 배포 환경별 설정

### **개발 환경** (Development)

```env
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development
MONGODB_URI=mongodb://localhost:27017/youth_policy_dev
OPENAI_API_KEY=sk-dev-key
```

### **스테이징 환경** (Staging)

```env
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=staging
MONGODB_URI=mongodb+srv://staging-user:password@staging-cluster.mongodb.net/
OPENAI_API_KEY=sk-staging-key
```

### **프로덕션 환경** (Production)

```env
DEBUG=False
LOG_LEVEL=WARNING
ENVIRONMENT=production
MONGODB_URI=mongodb+srv://prod-user:secure-password@prod-cluster.mongodb.net/
OPENAI_API_KEY=sk-prod-key
SECRET_KEY=super-secure-production-key
```

---

## 📈 모니터링 및 유지보수

### **로그 모니터링**

```bash
# 로그 레벨별 확인
grep "ERROR" logs/*.log    # 에러 로그 확인
grep "WARNING" logs/*.log  # 경고 로그 확인

# 실시간 로그 모니터링
tail -f logs/application.log
```

### **성능 모니터링**

```bash
# CPU 사용률 확인
top -p $(pgrep -f uvicorn)

# 메모리 사용률 확인
ps -o pid,ppid,%mem,rss,vsz,command -p $(pgrep -f uvicorn)

# 네트워크 연결 확인
netstat -tulnp | grep :8000
```

### **데이터베이스 모니터링**

```bash
# MongoDB 연결 수 확인
# MongoDB Atlas 대시보드에서 모니터링

# 응답 시간 확인
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

---

## 🚨 트러블슈팅 가이드

### **일반적인 문제들**

1. **서버 시작 실패**
   ```
   문제: ModuleNotFoundError
   해결: pip install -r requirements.txt

   문제: Port already in use
   해결: lsof -ti:8000 | xargs kill -9
   ```

2. **MongoDB 연결 실패**
   ```
   문제: Connection timeout
   해결: MongoDB URI 및 네트워크 설정 확인

   문제: Authentication failed
   해결: 사용자명/비밀번호 확인, IP 허용 목록 확인
   ```

3. **OpenAI API 오류**
   ```
   문제: API key not found
   해결: OPENAI_API_KEY 환경 변수 설정

   문제: Rate limit exceeded
   해결: 요청 빈도 조절 또는 API 플랜 업그레이드
   ```

### **응급 복구 절차**

1. **서비스 중단 시**
   ```bash
   # 1. 프로세스 확인
   ps aux | grep uvicorn

   # 2. 프로세스 종료
   pkill -f uvicorn

   # 3. 서비스 재시작
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **데이터베이스 연결 실패 시**
   ```bash
   # 1. Fallback 모드로 서비스 유지 (자동)
   # 2. MongoDB 연결 상태 확인
   # 3. 연결 복구 후 서비스 정상화
   ```

---

## ✅ 최종 배포 승인 체크리스트

### **필수 요구사항 (Must Have)**
- [ ] 모든 Agent (1-5) 정상 작동
- [ ] MongoDB 연결 또는 Fallback 모드 작동
- [ ] API 응답 시간 5초 이내
- [ ] 보안 설정 완료 (.env 파일 보안)
- [ ] 에러 처리 정상 작동

### **권장 요구사항 (Should Have)**
- [ ] OpenAI API 연동 (GPT 기능 활성화)
- [ ] 실제 정책 데이터 10개 이상
- [ ] 로그 시스템 설정
- [ ] 모니터링 시스템 구축

### **선택 요구사항 (Nice to Have)**
- [ ] 로드 밸런서 설정
- [ ] Redis 캐시 연동
- [ ] CI/CD 파이프라인 구축
- [ ] 알림 시스템 연동

---

## 🎉 배포 완료 후 확인사항

### **서비스 정상 작동 확인**

```bash
# 1. 헬스 체크
curl http://your-domain.com/health

# 2. API 문서 접근
open http://your-domain.com/docs

# 3. 샘플 추천 요청
curl -X POST http://your-domain.com/api/orchestrator \
  -H "Content-Type: application/json" \
  -d '{"age":25,"region":"서울","income":3000,"employment":"구직자","interest":"일자리"}'
```

### **성능 벤치마크**

- **응답 시간**: < 5초 (목표 달성 시 ✅)
- **동시 사용자**: 100명 (목표)
- **가용성**: 99.9% (목표)

---

**배포 준비 완료!** 🚀

이 체크리스트를 모두 완료하면 청년 정책 추천 시스템을 안전하고 안정적으로 배포할 수 있습니다.

**문의**: contact@youth-policy.kr
**문서 버전**: 1.0.0
**최종 업데이트**: 2026년 1월 9일