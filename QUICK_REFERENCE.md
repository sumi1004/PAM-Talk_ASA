# PAM-Talk 디지털 쿠폰 빠른 참조 가이드

## 🚀 5분 빠른 시작

### 1. 설치 (2분)
```bash
cd journal1211
pip install py-algorand-sdk flask flask-cors
```

### 2. 키 생성 (1분)
```bash
python security/keys_management_fixed.py
```

### 3. 테스트 (1분)
```bash
python test_system.py
# 결과: [PASS] [PASS] [PASS]
```

### 4. 데모 실행 (1분)
```bash
python start_demo.py
# 브라우저: http://localhost:8000
```

---

## 📋 자주 사용하는 명령어

### 시스템 테스트
```bash
python test_system.py
```

### 데모 대시보드
```bash
python start_demo.py
# http://localhost:8000
```

### API 서버
```bash
python api/coupon_api.py
# http://localhost:5000
```

### 보상 계산 시뮬레이션
```bash
python policies/reward_calculator.py
```

### 불변식 검증
```bash
python verification/invariants.py
```

---

## 💰 차등 보상 계산표

| 조건 | 소득 | 지역 | 활동 | 결과 |
|------|------|------|------|------|
| 최대 | 저소득 (1.5x) | 농어촌 (1.3x) | 탄소중립 (2.0x) | **3,900** (290% ↑) |
| 평균 | 중소득 (1.2x) | 도농복합 (1.15x) | 로컬푸드 (1.2x) | **1,656** (65% ↑) |
| 기본 | 고소득 (1.0x) | 도시 (1.0x) | 기본 (1.0x) | **1,000** (0% ↑) |

### 빠른 계산

```
최종 = 기본 × 소득 가중치 × 지역 가중치 × 활동 가중치

예: 1,000 × 1.5 × 1.3 × 2.0 = 3,900
```

---

## 🔑 M/R/F/C 권한 요약

| 권한 | 역할 | 다중서명 | 용도 |
|------|------|---------|------|
| **M** (Manager) | 정책 변경 | 2-of-3 | 메타데이터 수정 |
| **R** (Reserve) | 쿠폰 발급 | 단일 | 예산 관리 |
| **F** (Freeze) | 계정 동결 | 2-of-3 | 부정 의심 시 |
| **C** (Clawback) | 강제 회수 | 2-of-2 | 부정수급 회수 |

---

## 🌐 API 빠른 참조

### 기본 URL
```
http://localhost:5000
```

### 주요 엔드포인트

#### 잔액 조회
```bash
curl http://localhost:5000/api/coupon/balance/GKISL2MHRKU5...
```

#### 보상 계산
```bash
curl -X POST http://localhost:5000/api/coupon/calculate-reward \
  -H "Content-Type: application/json" \
  -d '{"base_amount":1000,"income_level":"low","region_type":"rural","activity_type":"carbon_neutral"}'
```

#### 예산 현황
```bash
curl http://localhost:5000/api/coupon/budget/status?period=2025-Q1
```

#### 불변식 검증
```bash
curl -X POST http://localhost:5000/api/coupon/verify-invariants
```

---

## 🔧 문제 해결 치트시트

### 오류별 해결

| 오류 | 원인 | 해결 |
|------|------|------|
| `No module named 'algosdk'` | 패키지 미설치 | `pip install py-algorand-sdk` |
| `Account not opted in` | Opt-in 안 함 | `asa.opt_in(...)` 실행 |
| `Insufficient balance` | ALGO 부족 | TestNet Faucet에서 받기 |
| `UnicodeEncodeError` | Windows 인코딩 | `*_fixed.py` 사용 |
| `Threshold not met` | 서명 부족 | 필요한 수만큼 서명 |

### TestNet ALGO 받기
```
https://bank.testnet.algorand.network/

주소 입력 → Dispense → 10 ALGO 수령
```

---

## 📊 시스템 상태 확인

### Reserve 계정 잔액
```python
from algosdk.v2client import algod

client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
info = client.account_info("RESERVE_ADDRESS")
print(f"Balance: {info['amount'] / 1_000_000} ALGO")
```

### ASA 정보 조회
```python
asset_info = client.asset_info(ASSET_ID)
print(f"Total Supply: {asset_info['params']['total']}")
```

### 불변식 빠른 체크
```python
from verification.invariants import InvariantVerifier

verifier = InvariantVerifier(client, asset_id)
results = verifier.verify_all_invariants()
print("All passed:", results['all_passed'])
```

---

## 🎯 프로젝트 구조 한눈에

```
journal1211/
├── security/          # 키 관리, 다중서명
├── contracts/         # ASA, Reserve
├── policies/          # 차등 보상
├── verification/      # 불변식
├── governance/        # 정책 메타데이터
├── api/               # REST API
├── config/            # 설정 (⚠️ Git 제외)
├── tests/             # 테스트
└── docs/              # 문서
```

---

## 🔐 보안 체크리스트

### ✅ 해야 할 것
- [x] `config/keys_secure.json` 백업
- [x] `.gitignore` 확인
- [x] 환경 변수 사용
- [x] HTTPS 사용 (프로덕션)
- [x] API 인증 추가
- [x] Rate Limiting 설정

### ❌ 하지 말아야 할 것
- [ ] Private key Git 커밋
- [ ] `.env` 파일 공유
- [ ] TestNet 키로 MainNet 사용
- [ ] HTTP로 프로덕션 운영
- [ ] 키를 코드에 하드코딩

---

## 📞 긴급 연락처

### 기술 지원
- 📧 support@pam-talk.com
- 🐛 GitHub Issues
- 📚 `USER_MANUAL.md` 참조

### 블록체인 관련
- 🌐 Algorand Developer Portal
- 🔍 AlgoExplorer (TestNet)
- 💧 TestNet Faucet

---

## 💡 팁 & 트릭

### 성능 향상
```python
# 캐싱 사용
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function():
    ...
```

### 배치 처리
```python
# 여러 트랜잭션 한 번에
from algosdk.transaction import assign_group_id

txns = [txn1, txn2, txn3]
assign_group_id(txns)
# Atomic Transfer (모두 성공 또는 모두 실패)
```

### 로그 레벨 조정
```bash
export LOG_LEVEL=DEBUG
python api/coupon_api.py
```

---

## 🎓 학습 경로

### 초급 (1일)
1. ✅ 시스템 설치
2. ✅ 키 생성
3. ✅ 테스트 실행
4. ✅ 데모 대시보드 확인

### 중급 (3일)
1. ✅ API 사용법
2. ✅ 차등 보상 이해
3. ✅ 불변식 검증
4. ✅ 다중서명 실습

### 고급 (1주)
1. ✅ ASA 토큰 생성
2. ✅ 정책 커스터마이징
3. ✅ MainNet 배포
4. ✅ 모니터링 설정

---

## 📖 추가 문서

| 문서 | 용도 |
|------|------|
| `USER_MANUAL.md` | 전체 사용 설명서 |
| `DEPLOYMENT_GUIDE.md` | 배포 가이드 |
| `TESTNET_DEMO_GUIDE.md` | TestNet 데모 |
| `README.md` | 프로젝트 소개 |

---

**빠른 질문? USER_MANUAL.md의 FAQ 섹션을 확인하세요!**
