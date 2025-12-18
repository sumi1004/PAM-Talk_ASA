# PAM-Talk 디지털 쿠폰 시스템 사용 설명서

## 📚 목차

1. [시스템 소개](#시스템-소개)
2. [설치 및 환경 설정](#설치-및-환경-설정)
3. [기본 개념](#기본-개념)
4. [사용자 가이드](#사용자-가이드)
5. [관리자 가이드](#관리자-가이드)
6. [API 레퍼런스](#api-레퍼런스)
7. [문제 해결](#문제-해결)
8. [FAQ](#faq)

---

## 시스템 소개

### PAM-Talk 디지털 쿠폰이란?

PAM-Talk 디지털 쿠폰은 **시민참여형 ESG 보상정책**을 위한 블록체인 기반 디지털 쿠폰 시스템입니다.

#### 핵심 특징

- 🔐 **블록체인 보안**: Algorand 블록체인 기반 위변조 방지
- 💰 **차등 보상**: 소득·지역·행동에 따라 최대 3.9배 차등 지급
- 🏛️ **투명한 거버넌스**: 다중서명 기반 권한 분리 (M/R/F/C)
- 📊 **자동 감사**: 불변식 기반 실시간 검증
- ♻️ **탄소중립 지원**: 탄소 감축 활동 측정·보상

#### 사용 대상

- **시민**: ESG 활동 참여 후 디지털 쿠폰 수령
- **가맹점**: 쿠폰 결제 수락 및 정산
- **지자체**: 예산 관리 및 정책 운영
- **감사기관**: 부정수급 모니터링 및 회수

---

## 설치 및 환경 설정

### 시스템 요구사항

| 구분 | 요구사항 |
|------|---------|
| 운영체제 | Windows 10/11, macOS, Linux |
| Python | 3.8 이상 |
| 네트워크 | 인터넷 연결 필수 (Algorand TestNet) |
| 메모리 | 최소 2GB RAM |
| 디스크 | 최소 500MB 여유 공간 |

### Step 1: 프로그램 다운로드

```bash
# Git으로 다운로드
git clone https://github.com/your-org/pam-talk-coupon.git
cd pam-talk-coupon/journal1211

# 또는 ZIP 파일 다운로드 후 압축 해제
```

### Step 2: 패키지 설치

```bash
pip install -r requirements.txt
```

**설치되는 패키지:**
- `py-algorand-sdk`: Algorand 블록체인 연동
- `flask`: 웹 API 서버
- `flask-cors`: API 보안

### Step 3: 초기 설정

```bash
# M/R/F/C 키 생성
python security/keys_management_fixed.py
```

**출력 예시:**
```
============================================================
PAM-Talk Digital Coupon - M/R/F/C Key Generator
============================================================
[OK] MANAGER #1 (Government): GVQJ7BNRCWOD...
[OK] RESERVE (Finance): GKISL2MHRKU5...
...
[SUCCESS] M/R/F/C Keys Generated!
```

### Step 4: 설정 확인

```bash
# 시스템 테스트
python test_system.py
```

**예상 결과:**
```
[PASS] Key Management
[PASS] Reward Calculator
[PASS] Reserve Manager

All tests passed!
```

---

## 기본 개념

### 1. M/R/F/C 권한 구조

PAM-Talk은 4개 권한으로 분리된 보안 구조를 사용합니다.

| 권한 | 영문 | 역할 | 다중서명 |
|------|------|------|---------|
| **M** | Manager | 정책 변경, 메타데이터 수정 | 2-of-3 |
| **R** | Reserve | 쿠폰 발급 및 예산 관리 | 단일 |
| **F** | Freeze | 계정 동결 (부정 의심 시) | 2-of-3 |
| **C** | Clawback | 쿠폰 강제 회수 (부정수급 확정 시) | 2-of-2 |

#### 왜 권한을 분리하나요?

```
예시: 부정수급 발견 시

1. Freeze 권한자 (감사기관 2명)가 계정 동결
2. 조사 진행
3. Clawback 권한자 (운영기관 + 감사기관)가 쿠폰 회수

→ 단일 기관의 독단적 결정 방지
→ 견제와 균형 확보
```

### 2. 쿠폰 수명주기

```
S0: 예산 배정
  ↓
S1: 쿠폰 생성 (Reserve 계정에 보관)
  ↓
S2: 발급 준비 (정책 검증)
  ↓
S3: 시민 수령 (Opt-in + Transfer)
  ↓
S4: 사용·정산 (가맹점 결제)
  ↓
S5: 정상 소멸 (만료)
  ↓
S6: 강제 회수 (부정수급 시 Clawback)
```

### 3. 차등 보상 공식

```
최종 보상 = 기본 보상 × 소득 가중치 × 지역 가중치 × 행동 가중치
```

#### 가중치 표

**소득 분위 (Income)**

| 소득 수준 | 해당 분위 | 가중치 |
|----------|----------|--------|
| 저소득 | 1~3분위 | 1.5배 |
| 중소득 | 4~7분위 | 1.2배 |
| 고소득 | 8~10분위 | 1.0배 |

**지역 (Region)**

| 지역 유형 | 가중치 |
|----------|--------|
| 농어촌 | 1.3배 |
| 도농복합 | 1.15배 |
| 도시권 | 1.0배 |

**행동 유형 (Activity)**

| 활동 | 가중치 |
|------|--------|
| 탄소중립 활동 | 2.0배 |
| 재활용 | 1.5배 |
| 에너지 절약 | 1.4배 |
| 대중교통 이용 | 1.3배 |
| 로컬푸드 구매 | 1.2배 |
| 기본 활동 | 1.0배 |

#### 계산 예시

**케이스 1: 최대 보상**
- 저소득(1.5) + 농어촌(1.3) + 탄소중립(2.0)
- 1,000 × 1.5 × 1.3 × 2.0 = **3,900 쿠폰**
- 보너스: +2,900 (290%)

**케이스 2: 평균 보상**
- 중소득(1.2) + 도농복합(1.15) + 로컬푸드(1.2)
- 1,000 × 1.2 × 1.15 × 1.2 = **1,656 쿠폰**
- 보너스: +656 (65.6%)

**케이스 3: 기본 보상**
- 고소득(1.0) + 도시(1.0) + 기본(1.0)
- 1,000 × 1.0 × 1.0 × 1.0 = **1,000 쿠폰**
- 보너스: 0

### 4. 불변식 검증

시스템은 4가지 불변식을 자동으로 검증합니다.

#### 불변식 1: 자산 보존
```
총 발행량 = Reserve 잔량 + 시민 보유 + 가맹점 보유 + 회수 잔량
```

#### 불변식 2: 1인 한도 준수
```
사용자별 누적 발급량 ≤ 정책 최대치
```

#### 불변식 3: 회수 계정 잔량
```
회수 후 회수 계정 잔량 = 0
(회수된 쿠폰은 즉시 소각 또는 재배분)
```

#### 불변식 4: 감사 증적
```
정책 버전별 증빙 해시 ≥ 1건
(모든 정책 변경은 블록체인에 기록)
```

---

## 사용자 가이드

### 시민 (쿠폰 수령자)

#### Step 1: 쿠폰 수령 자격 확인

**필요 조건:**
- ✅ Algorand 지갑 계정 (예: Pera Wallet, MyAlgo)
- ✅ 최소 0.1 ALGO (Opt-in 수수료)
- ✅ ESG 활동 증빙 (탄소 절약, 로컬푸드 구매 등)

#### Step 2: 쿠폰 Opt-in (수령 동의)

**웹 인터페이스:**
```
1. PAM-Talk 웹사이트 접속
2. "쿠폰 받기" 클릭
3. 지갑 연결 (Pera Wallet 등)
4. Opt-in 트랜잭션 서명
```

**Python 코드 (개발자용):**
```python
from contracts.esg_coupon_asa import ESGCouponASA

asa = ESGCouponASA()
result = asa.opt_in(
    user_address="YOUR_ADDRESS",
    user_private_key="YOUR_PRIVATE_KEY",
    asset_id=123456789  # PAM 쿠폰 Asset ID
)

print(f"Opt-in 완료: {result['tx_id']}")
```

#### Step 3: 활동 등록 및 보상 계산

**웹에서 활동 등록:**
```
1. "활동 등록" 메뉴 선택
2. 활동 유형 선택 (예: 탄소중립 활동)
3. 증빙 자료 업로드 (영수증, 사진 등)
4. 제출
```

**예상 보상 미리보기:**
```
활동: 지역 유기농 농산물 구매
증빙: 영수증 사진

계산:
- 기본 보상: 1,000 쿠폰
- 소득 분위: 3분위 (저소득) → ×1.5
- 지역: 농어촌 → ×1.3
- 활동: 로컬푸드 구매 → ×1.2

예상 보상: 1,000 × 1.5 × 1.3 × 1.2 = 2,340 쿠폰
```

#### Step 4: 쿠폰 수령 확인

**지갑에서 확인:**
```
Pera Wallet 또는 MyAlgo 열기
→ Assets 탭
→ "PAM-TALK-ESG-2025" 찾기
→ 잔액 확인
```

**웹에서 확인:**
```
PAM-Talk 웹사이트
→ "내 쿠폰" 메뉴
→ 잔액: 2,340 쿠폰
```

#### Step 5: 쿠폰 사용

**가맹점에서 결제:**
```
1. 가맹점에서 상품 선택
2. "PAM 쿠폰 결제" 선택
3. 사용할 쿠폰 수량 입력
4. 지갑에서 트랜잭션 서명
5. 결제 완료!
```

**할인율:**
- 쿠폰 1개 = 1,000원 할인
- 최대 사용 한도: 구매금액의 50%

**소각 규칙:**
- 사용한 쿠폰의 10%는 자동 소각
- 예: 100 쿠폰 사용 → 10개 소각, 90개 가맹점에 지급

### 가맹점 (쿠폰 수락 점포)

#### Step 1: 가맹점 등록

**필요 서류:**
- 사업자등록증
- 통장 사본
- Algorand 지갑 주소

**등록 절차:**
```
1. PAM-Talk 가맹점 신청서 제출
2. 심사 (3~5일)
3. 승인 후 가맹점 ID 발급
4. POS 시스템 연동 (선택)
```

#### Step 2: 쿠폰 결제 수락

**수동 결제:**
```
1. 고객에게 지갑 주소 요청
2. 결제 금액 확인
3. PAM-Talk 가맹점 앱에서 "결제 요청"
4. 고객이 지갑에서 승인
5. 완료 확인
```

**POS 연동 결제:**
```
1. POS에서 결제 금액 입력
2. "PAM 쿠폰" 버튼 클릭
3. QR 코드 생성
4. 고객이 QR 스캔 → 지갑에서 승인
5. 자동 완료
```

#### Step 3: 정산 받기

**정산 주기:**
- 직불형: 즉시 (트랜잭션 완료와 동시)
- 후불형: 주 1회 (매주 금요일)

**정산 금액:**
```
고객이 사용한 쿠폰 - 10% (소각분)

예: 고객이 100 쿠폰 사용
→ 가맹점 수령: 90 쿠폰
→ 소각: 10 쿠폰
```

**쿠폰 → 현금 전환:**
```
1. PAM-Talk 웹사이트 로그인
2. "정산 신청" 메뉴
3. 전환할 쿠폰 수량 입력
4. 은행 계좌 확인
5. 신청 (2~3일 후 입금)
```

### 지자체 (정책 관리자)

#### Step 1: 예산 설정

**연간 예산 배정:**
```python
from contracts.reserve_manager import ReserveManager

manager = ReserveManager()

# 2025년 1분기 예산 설정
manager.set_budget(
    period="2025-Q1",
    total_budget=10000000,      # 1,000만 쿠폰
    per_person_limit=50000      # 1인당 5만 쿠폰
)
```

**예산 현황 조회:**
```python
status = manager.get_budget_status("2025-Q1")

print(f"총 예산: {status['total_budget']:,}")
print(f"사용: {status['allocated']:,}")
print(f"잔액: {status['remaining']:,}")
print(f"사용률: {status['utilization_rate']:.1f}%")
```

#### Step 2: 정책 변경

**차등 보상 비율 조정:**
```python
# policies/reward_calculator.py 수정

INCOME_MULTIPLIERS = {
    IncomeLevel.LOW: 1.8,      # 1.5 → 1.8로 상향
    IncomeLevel.MIDDLE: 1.3,   # 1.2 → 1.3으로 상향
    IncomeLevel.HIGH: 1.0
}
```

**정책 문서 업데이트:**
```python
from governance.policy_metadata import PolicyMetadataManager

manager = PolicyMetadataManager()

# 새 정책 문서 생성
doc = manager.create_policy_document(
    title="2025년 2분기 PAM 쿠폰 운영 지침 (개정)",
    content="... 정책 내용 ...",
    version="v1.1",
    effective_date="2025-04-01",
    expiry_date="2025-06-30",
    issuer="서울특별시",
    metadata={...}
)

# 블록체인에 해시 앵커링
policy_hash = manager.calculate_metadata_hash(...)
manager.anchor_hash_to_blockchain(policy_hash, asset_id)
```

#### Step 3: 발급 승인

**활동 심사 및 승인:**
```
1. 관리자 대시보드 접속
2. "승인 대기" 목록 확인
3. 활동 증빙 검토
4. 승인 또는 반려
```

**자동 발급:**
```python
# API를 통한 자동 발급 (승인 후)
import requests

response = requests.post('http://localhost:5000/api/coupon/issue', json={
    "user_id": "citizen001",
    "user_address": "ALGORAND_ADDRESS",
    "base_amount": 1000,
    "income_level": "low",
    "region_type": "rural",
    "activity_type": "carbon_neutral",
    "reason": "지역 농산물 구매"
})

print(response.json())
# → {"success": true, "amount_issued": 3900, "tx_id": "..."}
```

#### Step 4: 모니터링

**실시간 대시보드:**
```
http://localhost:8000

확인 가능 항목:
- 총 발급량 / 예산 잔액
- 상위 수혜자 목록
- 가맹점별 사용 현황
- 일별 발급/사용 그래프
```

**통계 조회:**
```python
# 상위 수혜자
top_users = manager.get_top_recipients(limit=10)

for user in top_users:
    print(f"{user['user_id']}: {user['total_issued']:,} 쿠폰")
```

### 감사기관 (부정 방지)

#### Step 1: 실시간 모니터링

**의심 거래 탐지:**
```python
from verification.invariants import InvariantVerifier
from algosdk.v2client import algod

algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
verifier = InvariantVerifier(algod_client, asset_id)

# 불변식 검증
results = verifier.verify_all_invariants()

if not results['all_passed']:
    print("⚠️ 이상 징후 발견!")
    print(results['limit_compliance']['violations'])
```

**한도 초과자 확인:**
```python
# 1인당 한도 초과자 조회
violations = results['limit_compliance']['violations']

for v in violations:
    print(f"사용자: {v['user_id']}")
    print(f"발급량: {v['total_issued']} (한도: {v['limit']})")
    print(f"초과: {v['excess']}")
```

#### Step 2: 계정 동결 (Freeze)

**의심 계정 동결:**
```python
from security.multisig_handler import MultiSigHandler

handler = MultiSigHandler(algod_client)

# Freeze 다중서명 (2-of-3 필요)
result = handler.freeze_with_multisig(
    msig=freeze_msig,
    asset_id=asset_id,
    target_address="의심_사용자_주소",
    freeze_state=True,  # 동결
    signers_private_keys=[
        auditor1_key,    # 감사기관
        supervisor_key   # 상위 감독기관
    ]
)

print(f"동결 완료: {result['tx_id']}")
```

**동결 해제:**
```python
# 조사 완료 후 무혐의 판정 시
result = handler.freeze_with_multisig(
    msig=freeze_msig,
    asset_id=asset_id,
    target_address="조사_완료_사용자",
    freeze_state=False,  # 해제
    signers_private_keys=[auditor1_key, supervisor_key]
)
```

#### Step 3: 쿠폰 회수 (Clawback)

**부정수급 확정 시:**
```python
# Clawback 다중서명 (2-of-2 필요: 운영 + 감사)
result = handler.clawback_with_multisig(
    msig=clawback_msig,
    asset_id=asset_id,
    target_address="부정수급자_주소",
    recovery_address="회수_계정_주소",
    amount=5000,  # 회수할 쿠폰 수
    signers_private_keys=[
        operations_key,   # 운영기관
        audit_key         # 감사기관
    ]
)

print(f"회수 완료: {amount} 쿠폰")
print(f"TX ID: {result['tx_id']}")
```

**회수 내역 기록:**
```python
# 회수 사유 및 증빙 기록
record = {
    "target_user": "부정수급자 ID",
    "amount_clawed": 5000,
    "reason": "허위 증빙 제출",
    "evidence": "증빙 파일 해시",
    "approvers": ["운영기관", "감사기관"],
    "tx_id": result['tx_id'],
    "timestamp": datetime.now().isoformat()
}

# 데이터베이스에 저장
save_clawback_record(record)
```

---

## 관리자 가이드

### 시스템 관리자

#### 서버 시작/중지

**데모 대시보드:**
```bash
# 시작
python start_demo.py

# 브라우저에서 열기
http://localhost:8000

# 중지
Ctrl + C
```

**API 서버:**
```bash
# 개발 모드
python api/coupon_api.py

# 프로덕션 모드
gunicorn -w 4 -b 0.0.0.0:5000 api.coupon_api:app
```

#### 백업

**키 파일 백업:**
```bash
# 안전한 위치에 백업
cp config/keys_secure.json ~/backup/keys_secure_$(date +%Y%m%d).json

# 암호화 저장 권장
gpg -c ~/backup/keys_secure_20250101.json
```

**데이터베이스 백업:**
```bash
# SQLite
cp config/budget_config.json ~/backup/

# PostgreSQL (프로덕션)
pg_dump pamtalk_db > backup_$(date +%Y%m%d).sql
```

#### 로그 관리

**로그 확인:**
```bash
# API 서버 로그
tail -f coupon_api.log

# 에러만 필터링
grep ERROR coupon_api.log
```

**로그 로테이션:**
```bash
# logrotate 설정 (Linux)
/var/log/pamtalk/*.log {
    daily
    rotate 7
    compress
    missingok
}
```

### 데이터베이스 관리자

#### 데이터 조회

**발급 내역:**
```sql
SELECT
    user_id,
    SUM(amount) as total_issued,
    COUNT(*) as issue_count
FROM issuance_records
WHERE timestamp >= '2025-01-01'
GROUP BY user_id
ORDER BY total_issued DESC
LIMIT 10;
```

**가맹점 정산:**
```sql
SELECT
    merchant_id,
    SUM(amount * 0.9) as settlement_amount,
    COUNT(*) as transaction_count
FROM merchant_transactions
WHERE settlement_date IS NULL
GROUP BY merchant_id;
```

#### 성능 최적화

**인덱스 생성:**
```sql
CREATE INDEX idx_user_timestamp
ON issuance_records(user_id, timestamp);

CREATE INDEX idx_merchant_date
ON merchant_transactions(merchant_id, transaction_date);
```

**쿼리 튜닝:**
```sql
EXPLAIN ANALYZE
SELECT ...
-- 실행 계획 확인 후 최적화
```

---

## API 레퍼런스

### 엔드포인트 목록

#### 1. 헬스 체크

```http
GET /health
```

**응답:**
```json
{
  "status": "healthy",
  "service": "PAM-Talk Digital Coupon API",
  "version": "1.0.0"
}
```

#### 2. 쿠폰 정보 조회

```http
GET /api/coupon/info
```

**응답:**
```json
{
  "success": true,
  "data": {
    "asset_id": 123456789,
    "name": "PAM-TALK-ESG-2025",
    "unit_name": "ESG-CPN",
    "total_supply": 1000000,
    "decimals": 0,
    "manager": "K5FHP4USS27...",
    "reserve": "GKISL2MHRKU...",
    "freeze": "242OQOKZN6U...",
    "clawback": "4ASFZCRPHKZ..."
  }
}
```

#### 3. 잔액 조회

```http
GET /api/coupon/balance/{address}
```

**파라미터:**
- `address`: Algorand 지갑 주소

**응답:**
```json
{
  "success": true,
  "data": {
    "address": "GKISL2MHRKU...",
    "asset_id": 123456789,
    "balance": 5000
  }
}
```

#### 4. 보상 계산 (미리보기)

```http
POST /api/coupon/calculate-reward
```

**요청 본문:**
```json
{
  "base_amount": 1000,
  "income_level": "low",
  "region_type": "rural",
  "activity_type": "carbon_neutral"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "base_amount": 1000,
    "income_multiplier": 1.5,
    "region_multiplier": 1.3,
    "activity_multiplier": 2.0,
    "total_multiplier": 3.9,
    "final_amount": 3900,
    "bonus_amount": 2900
  }
}
```

#### 5. 쿠폰 발급

```http
POST /api/coupon/issue
```

**요청 본문:**
```json
{
  "user_id": "citizen001",
  "user_address": "ALGORAND_ADDRESS",
  "base_amount": 1000,
  "income_level": "low",
  "region_type": "rural",
  "activity_type": "carbon_neutral",
  "reason": "탄소중립 활동 참여"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "record_id": "ISS-000001",
    "user_id": "citizen001",
    "amount_issued": 3900,
    "reward_breakdown": {...},
    "tx_id": "ALGORAND_TX_ID"
  }
}
```

#### 6. 예산 현황

```http
GET /api/coupon/budget/status?period=2025-Q1
```

**응답:**
```json
{
  "success": true,
  "data": {
    "period": "2025-Q1",
    "total_budget": 1000000,
    "allocated": 125000,
    "remaining": 875000,
    "utilization_rate": 12.5,
    "per_person_limit": 5000
  }
}
```

#### 7. 사용자 발급 내역

```http
GET /api/coupon/user/{user_id}/summary
```

**응답:**
```json
{
  "success": true,
  "data": {
    "user_id": "citizen001",
    "total_issued": 15000,
    "issuance_count": 8,
    "records": [
      {
        "record_id": "ISS-000001",
        "amount": 3900,
        "reason": "탄소중립 활동",
        "timestamp": "2025-01-15T10:30:00"
      },
      ...
    ]
  }
}
```

#### 8. 불변식 검증

```http
POST /api/coupon/verify-invariants
```

**응답:**
```json
{
  "success": true,
  "data": {
    "asset_conservation": {
      "passed": true,
      "total_supply": 1000000,
      "total_distributed": 1000000
    },
    "limit_compliance": {
      "passed": true,
      "violations_count": 0
    },
    "clawback_compliance": {
      "passed": true,
      "balance": 0
    },
    "audit_trail": {
      "passed": true
    },
    "all_passed": true
  }
}
```

#### 9. 상위 수혜자 조회

```http
GET /api/admin/top-recipients?limit=10
```

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "user_id": "citizen001",
      "total_issued": 50000
    },
    {
      "user_id": "citizen002",
      "total_issued": 45000
    },
    ...
  ]
}
```

### 에러 코드

| 코드 | 의미 | 해결 방법 |
|------|------|----------|
| 400 | 잘못된 요청 | 요청 본문 형식 확인 |
| 401 | 인증 실패 | API 키 확인 |
| 403 | 권한 없음 | 예산 한도 또는 권한 확인 |
| 404 | 리소스 없음 | URL 또는 ID 확인 |
| 429 | 요청 과다 | 잠시 후 재시도 |
| 500 | 서버 오류 | 로그 확인 또는 관리자 문의 |

---

## 문제 해결

### 일반적인 문제

#### Q1: "No module named 'algosdk'" 오류

**원인:** Python 패키지 미설치

**해결:**
```bash
pip install py-algorand-sdk
```

#### Q2: TestNet ALGO를 받지 못함

**원인:** Faucet 일시적 문제

**해결:**
1. VPN 끄기
2. 5~10분 후 재시도
3. 다른 Faucet 사용: https://dispenser.testnet.aws.algodev.network/

#### Q3: "Account not opted in" 오류

**원인:** 사용자가 ASA Opt-in 안 함

**해결:**
```python
asa.opt_in(user_address, user_private_key, asset_id)
```

#### Q4: 다중서명 트랜잭션 실패

**원인:** 필요한 서명 수 부족

**해결:**
- Freeze (2-of-3): 최소 2개 서명
- Clawback (2-of-2): 반드시 2개 서명

#### Q5: Windows 인코딩 오류

**원인:** 이모지 출력 문제

**해결:**
`keys_management_fixed.py` 사용 (이모지 제거 버전)

#### Q6: API 응답 느림

**원인:** TestNet 네트워크 지연

**해결:**
- TestNet은 개발용이므로 지연 정상
- MainNet 사용 시 속도 개선
- 캐싱 활성화

### 로그 확인

**에러 발생 시:**
```bash
# API 로그
tail -f coupon_api.log | grep ERROR

# 시스템 로그
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

### 성능 튜닝

**API 응답 속도 개선:**
```python
# 캐싱 추가
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_summary(user_id):
    # ...
```

**데이터베이스 최적화:**
```sql
-- 인덱스 추가
CREATE INDEX idx_user_id ON issuance_records(user_id);

-- 쿼리 최적화
EXPLAIN ANALYZE SELECT ...;
```

---

## FAQ

### 시스템 일반

**Q: PAM-Talk 쿠폰은 실제 돈인가요?**

A: 아니요. 디지털 쿠폰은 가맹점에서만 사용 가능한 보상 포인트입니다. 가맹점은 정산 시 현금으로 전환할 수 있습니다.

**Q: 블록체인을 왜 사용하나요?**

A:
- 위변조 방지
- 투명한 거래 기록
- 자동 감사
- 탈중앙화 신뢰

**Q: TestNet과 MainNet의 차이는?**

A:
- **TestNet**: 개발·테스트용, 무료, 가짜 ALGO
- **MainNet**: 실제 운영, 실제 ALGO 필요

**Q: 쿠폰 유효기간은?**

A: 정책마다 다름 (예: 2025-01-01 ~ 2025-12-31)

### 기술적 질문

**Q: Algorand를 선택한 이유는?**

A:
- 빠른 속도 (4.5초 완결성)
- 저렴한 수수료 (0.001 ALGO)
- 높은 TPS (1,000+)
- 친환경 (탄소중립 블록체인)

**Q: M/R/F/C 키를 분실하면?**

A:
- **Manager**: 2-of-3이므로 1개 분실 시 복구 가능
- **Reserve**: 백업에서 복구 (백업 필수!)
- **Freeze**: 2-of-3이므로 1개 분실 시 복구 가능
- **Clawback**: 2-of-2이므로 1개 분실 시 재생성 필요

**Q: 불변식 검증은 언제 실행되나요?**

A:
- 주요 작업 후 자동 실행
- 관리자가 수동 실행 가능
- API `/verify-invariants` 호출

**Q: 차등 보상 비율은 변경 가능한가요?**

A: 네, 정책 관리자가 `reward_calculator.py` 수정 후 재배포

### 운영 질문

**Q: 하루에 몇 명까지 처리 가능한가요?**

A: Algorand TPS 기준 수만 명 동시 처리 가능

**Q: 가맹점 수수료는?**

A: 쿠폰의 10%는 자동 소각 (가맹점은 90% 수령)

**Q: 부정수급 기준은?**

A:
- 허위 증빙 제출
- 중복 신청
- 1인 한도 초과 시도
- 대리 신청

**Q: 쿠폰을 현금으로 바꿀 수 있나요?**

A:
- **시민**: 불가 (가맹점 사용만)
- **가맹점**: 가능 (정산 시 현금 전환)

---

## 부록

### A. 용어 사전

| 용어 | 설명 |
|------|------|
| **ASA** | Algorand Standard Asset - Algorand 블록체인 토큰 표준 |
| **Opt-in** | ASA를 받기 위한 사전 동의 절차 |
| **Freeze** | 계정 동결 - 쿠폰 이동 금지 |
| **Clawback** | 강제 회수 - 부정수급 쿠폰 회수 |
| **M/R/F/C** | Manager, Reserve, Freeze, Clawback 권한 |
| **불변식** | 항상 참이어야 하는 시스템 규칙 |
| **다중서명** | 여러 서명자의 승인이 필요한 트랜잭션 |
| **TestNet** | 테스트용 블록체인 네트워크 |
| **MainNet** | 실제 운영 블록체인 네트워크 |

### B. 참고 링크

**Algorand 공식 문서:**
- Developer Portal: https://developer.algorand.org/
- ASA Guide: https://developer.algorand.org/docs/get-details/asa/
- TestNet Faucet: https://bank.testnet.algorand.network/
- AlgoExplorer: https://testnet.algoexplorer.io/

**PAM-Talk 프로젝트:**
- GitHub: https://github.com/your-org/pam-talk-coupon
- 문서: `docs/DEPLOYMENT_GUIDE.md`
- 데모: http://localhost:8000

**지원:**
- 이메일: support@pam-talk.com
- 이슈 트래커: https://github.com/your-org/pam-talk-coupon/issues

### C. 변경 이력

**v1.0.0 (2025-01-15)**
- 초기 출시
- M/R/F/C 키 관리
- 차등 보상 시스템
- 불변식 검증
- REST API

---

## 문의하기

기술 지원이 필요하시면:

📧 **이메일**: support@pam-talk.com
🐛 **버그 리포트**: GitHub Issues
💬 **커뮤니티**: Discord 채널

---

**PAM-Talk Digital Coupon v1.0**
*시민참여형 ESG 보상, 블록체인으로 투명하게*
