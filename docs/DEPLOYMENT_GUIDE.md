# PAM-Talk 디지털 쿠폰 시스템 배포 가이드

## 목차

1. [사전 요구사항](#사전-요구사항)
2. [Phase 1: 키 생성](#phase-1-키-생성)
3. [Phase 2: ASA 토큰 배포](#phase-2-asa-토큰-배포)
4. [Phase 3: 예산 설정](#phase-3-예산-설정)
5. [Phase 4: API 서버 배포](#phase-4-api-서버-배포)
6. [Phase 5: 검증 및 테스트](#phase-5-검증-및-테스트)
7. [보안 고려사항](#보안-고려사항)
8. [문제 해결](#문제-해결)

---

## 사전 요구사항

### 소프트웨어

- Python 3.8+
- pip
- Git

### Algorand TestNet 준비

1. TestNet Faucet에서 ALGO 받기: https://bank.testnet.algorand.network/
2. 최소 10 ALGO 보유 권장

---

## Phase 1: 키 생성

### Step 1-1: 환경 설정

```bash
cd journal1211
pip install -r requirements.txt
```

### Step 1-2: M/R/F/C 키 생성

```bash
python security/keys_management.py --init
```

**출력 예시:**
```
🔐 M/R/F/C 키 구조 생성 중...
  ✓ MANAGER #1 (중앙정부): XXXXXXXXXX...
  ✓ MANAGER #2 (광역지자체): XXXXXXXXXX...
  ✓ MANAGER #3 (기술운영팀): XXXXXXXXXX...
  ✓ RESERVE (재정담당부서): XXXXXXXXXX...
  ✓ FREEZE #1 (감사기관): XXXXXXXXXX...
  ✓ FREEZE #2 (상위감독기관): XXXXXXXXXX...
  ✓ FREEZE #3 (내부감사팀): XXXXXXXXXX...
  ✓ CLAWBACK #1 (운영기관): XXXXXXXXXX...
  ✓ CLAWBACK #2 (감사기관): XXXXXXXXXX...

✅ M/R/F/C 키 생성 완료!
```

### Step 1-3: 키 검증

```bash
python security/keys_management.py --verify
```

### Step 1-4: 보안 조치

**중요!** `config/keys_secure.json` 파일을 안전하게 보관하세요.

```bash
# 파일 권한 제한 (Linux/Mac)
chmod 600 config/keys_secure.json

# 백업 생성
cp config/keys_secure.json config/keys_secure.json.backup

# .gitignore에 추가 확인
echo "config/keys_secure.json" >> .gitignore
```

---

## Phase 2: ASA 토큰 배포

### Step 2-1: Reserve 계정에 ALGO 충전

1. `config/keys_public.json`에서 Reserve 주소 확인
2. TestNet Faucet에서 해당 주소로 ALGO 전송
3. 최소 1 ALGO 보유 확인

```bash
# 잔액 확인 (AlgoExplorer TestNet)
https://testnet.algoexplorer.io/address/[RESERVE_ADDRESS]
```

### Step 2-2: ASA 토큰 생성

```bash
python contracts/esg_coupon_asa.py
```

**출력 예시:**
```
🪙 ESG 디지털 쿠폰 ASA 생성 중...
📤 트랜잭션 전송: TXXXXXXXXXXXXXXXXXXXXXXXXXXX
✅ ASA 생성 완료!
   Asset ID: 123456789
   Manager: XXXXXXXXXX...
   Reserve: XXXXXXXXXX...
   Freeze: XXXXXXXXXX...
   Clawback: XXXXXXXXXX...

✅ ASA 설정 저장: config/asa_config.json
```

### Step 2-3: ASA 정보 확인

```bash
# AlgoExplorer에서 확인
https://testnet.algoexplorer.io/asset/[ASSET_ID]
```

**확인 항목:**
- ✅ Total Supply: 1,000,000
- ✅ Decimals: 0
- ✅ Default Frozen: True
- ✅ Manager, Reserve, Freeze, Clawback 주소 일치

---

## Phase 3: 예산 설정

### Step 3-1: 예산 초기화

```bash
python contracts/reserve_manager.py
```

### Step 3-2: 예산 설정 확인

```python
from contracts.reserve_manager import ReserveManager

manager = ReserveManager()
status = manager.get_budget_status("2025-Q1")
print(status)
```

**출력 예시:**
```json
{
  "period": "2025-Q1",
  "total_budget": 1000000,
  "allocated": 0,
  "remaining": 1000000,
  "utilization_rate": 0.0,
  "per_person_limit": 5000
}
```

---

## Phase 4: API 서버 배포

### Step 4-1: 로컬 테스트

```bash
python api/coupon_api.py
```

**출력:**
```
============================================================
PAM-Talk 디지털 쿠폰 API 서버
============================================================
주소: http://localhost:5000
문서: http://localhost:5000/health
============================================================
```

### Step 4-2: API 테스트

```bash
# 헬스 체크
curl http://localhost:5000/health

# 쿠폰 정보 조회
curl http://localhost:5000/api/coupon/info

# 보상 계산
curl -X POST http://localhost:5000/api/coupon/calculate-reward \
  -H "Content-Type: application/json" \
  -d '{
    "base_amount": 1000,
    "income_level": "low",
    "region_type": "rural",
    "activity_type": "carbon_neutral"
  }'
```

### Step 4-3: 프로덕션 배포

#### Gunicorn 사용 (권장)

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 api.coupon_api:app
```

#### Docker 사용

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api.coupon_api:app"]
```

```bash
docker build -t pam-coupon-api .
docker run -p 5000:5000 pam-coupon-api
```

---

## Phase 5: 검증 및 테스트

### Step 5-1: 불변식 검증

```bash
python verification/invariants.py
```

### Step 5-2: 차등 보상 시뮬레이션

```bash
python policies/reward_calculator.py
```

**출력 예시:**
```
================================================================================
차등 보상 시뮬레이션
================================================================================

시나리오 1: 저소득 농어촌 탄소중립 활동
--------------------------------------------------------------------------------
기본: 1,000 → 최종: 3,900 (+2,900, ×3.90)

시나리오 2: 고소득 도시 기본 활동
--------------------------------------------------------------------------------
기본: 1,000 → 최종: 1,000 (+0, ×1.00)
```

### Step 5-3: 다중서명 테스트

```bash
python security/multisig_handler.py
```

### Step 5-4: 통합 테스트

```bash
pytest tests/
```

---

## 보안 고려사항

### 1. Private Key 관리

**절대 금지:**
- ❌ Git에 커밋
- ❌ 코드에 하드코딩
- ❌ 로그 출력
- ❌ 평문 저장

**권장 방법:**
- ✅ 환경 변수 사용
- ✅ HSM 사용 (프로덕션)
- ✅ AWS Secrets Manager / Azure Key Vault
- ✅ 암호화 저장

```python
# .env 파일 사용
import os
from dotenv import load_dotenv

load_dotenv()
RESERVE_PRIVATE_KEY = os.getenv("RESERVE_PRIVATE_KEY")
```

### 2. API 보안

```python
# API 키 인증 추가
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv("API_KEY"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/coupon/issue', methods=['POST'])
@require_api_key
def issue_coupon():
    # ...
```

### 3. Rate Limiting

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/coupon/issue', methods=['POST'])
@limiter.limit("10 per minute")
def issue_coupon():
    # ...
```

### 4. HTTPS 필수

프로덕션에서는 반드시 HTTPS 사용:

```bash
# Nginx 설정
server {
    listen 443 ssl;
    server_name api.pam-talk.com;

    ssl_certificate /etc/letsencrypt/live/api.pam-talk.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.pam-talk.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
    }
}
```

---

## 문제 해결

### Q1: "AssetConfigTxn failed" 오류

**원인:** Creator 계정에 ALGO 부족

**해결:**
```bash
# TestNet Faucet에서 ALGO 받기
https://bank.testnet.algorand.network/
```

### Q2: "Account not opted in" 오류

**원인:** 사용자가 ASA를 opt-in하지 않음

**해결:**
```python
# 사용자가 opt-in 실행
asa_service.opt_in(user_address, user_private_key, asset_id)
```

### Q3: 다중서명 실패

**원인:** threshold보다 적은 서명

**해결:**
- Freeze: 2-of-3 → 최소 2개 서명 필요
- Clawback: 2-of-2 → 반드시 2개 서명 필요

### Q4: 예산 한도 초과

**원인:** 1인당 한도 또는 전체 예산 초과

**해결:**
```python
# 예산 증액
manager.set_budget(
    period="2025-Q2",
    total_budget=2000000,
    per_person_limit=10000
)
```

---

## 모니터링

### 로그 수집

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coupon_api.log'),
        logging.StreamHandler()
    ]
)
```

### 메트릭 수집

```bash
pip install prometheus-flask-exporter
```

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

---

## 다음 단계

1. **MainNet 배포**: TestNet 테스트 완료 후
2. **모니터링 대시보드**: Grafana 연동
3. **자동화**: CI/CD 파이프라인 구축
4. **스케일링**: Kubernetes 배포

---

## 참고 자료

- [Algorand Developer Docs](https://developer.algorand.org/)
- [ASA Specification](https://developer.algorand.org/docs/get-details/asa/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PRD 문서](../README.md)

---

**배포 완료!** 🎉

문제가 있으면 이슈를 등록해주세요: https://github.com/pam-talk/digital-coupon/issues
