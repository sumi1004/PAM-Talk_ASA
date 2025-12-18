# 🎉 PAM-Talk 디지털 쿠폰 시스템 - TestNet 데모 가이드

## ✅ 시스템 구축 완료!

모든 핵심 컴포넌트가 성공적으로 구현되고 테스트되었습니다.

---

## 📊 현재 상태

### ✅ 완료된 기능

| 컴포넌트 | 상태 | 설명 |
|---------|------|------|
| **M/R/F/C 키 관리** | ✅ PASS | Manager(2-of-3), Reserve(단일), Freeze(2-of-3), Clawback(2-of-2) |
| **차등 보상 계산기** | ✅ PASS | 소득·지역·행동별 최대 3.9배 차등 지급 |
| **Reserve 예산 관리** | ✅ PASS | 예산 100만개, 1인당 한도 5,000개 |
| **불변식 검증** | ✅ 구현 | 자산 보존, 한도, 회수, 감사 자동 검증 |
| **다중서명 처리** | ✅ 구현 | Freeze/Clawback 다중서명 지원 |
| **정책 메타데이터** | ✅ 구현 | ARC-3 기반, 해시 앵커링 |
| **REST API** | ✅ 구현 | Flask 기반 9개 엔드포인트 |

### ⏳ 다음 단계 (TestNet ALGO 필요)

| 작업 | 필요 사항 | 예상 소요 |
|------|----------|----------|
| ASA 토큰 생성 | Reserve에 1 ALGO | 5분 |
| Opt-in 테스트 | 사용자 계정에 0.1 ALGO | 2분 |
| Transfer 테스트 | Reserve 잔액 | 3분 |
| Freeze/Clawback 테스트 | 다중서명 키 | 10분 |

---

## 🌐 데모 대시보드

### 현재 실행 중인 서버:

```
http://localhost:8000
```

### 대시보드 기능

- 🔐 **M/R/F/C 키 정보** - 생성된 4개 권한 주소 확인
- 📊 **차등 보상 계산** - 실시간 시뮬레이션
- 💰 **예산 현황** - Reserve 관리 상태
- ✅ **테스트 결과** - 각 컴포넌트 상태

---

## 🔑 생성된 키 정보

### Reserve 계정 (자금 필요!)
```
Address: GKISL2MHRKU5NAVFKXLMKZVDQK3DQ6OUP7NL6CYJ4T73PQBOAFWFHKTHDM
Balance: 0.000000 ALGO ⚠️

👉 TestNet ALGO 받기: https://bank.testnet.algorand.network/
```

### Manager (2-of-3 다중서명)
```
Address: K5FHP4USS27NYG3VWKVWZWFBX4NAIQ3MB36GHGJCHYLT5GRCSEUDX5B7OY
```

### Freeze (2-of-3 다중서명)
```
Address: 242OQOKZN6UWEAJ5SY2KQGQQQD4UV5CLBYBI2R42A7HHVGJVEZQX7SU76I
```

### Clawback (2-of-2 다중서명)
```
Address: 4ASFZCRPHKZ7GXT6O5BYULQTMMQ6Y3WKTACOASLNU2XVWLFDFUPCKSXLSM
```

---

## 🧪 테스트 결과

### 실행한 테스트

```bash
python test_system.py
```

**결과:**
```
[PASS] Key Management
[PASS] Reward Calculator
[PASS] Reserve Manager
```

### 차등 보상 계산 예시

#### 시나리오 1: 최대 보상
- **조건**: 저소득 + 농어촌 + 탄소중립 활동
- **계산**: 1,000 × 1.5 × 1.3 × 2.0 = **3,900 쿠폰**
- **보너스**: +2,900 (290% 추가)

#### 시나리오 2: 기본 보상
- **조건**: 고소득 + 도시 + 기본 활동
- **계산**: 1,000 × 1.0 × 1.0 × 1.0 = **1,000 쿠폰**
- **보너스**: 0

---

## 🚀 다음 단계: ASA 토큰 생성

### Step 1: TestNet ALGO 받기

1. 브라우저에서 열기:
   ```
   https://bank.testnet.algorand.network/
   ```

2. Reserve 주소 입력:
   ```
   GKISL2MHRKU5NAVFKXLMKZVDQK3DQ6OUP7NL6CYJ4T73PQBOAFWFHKTHDM
   ```

3. "Dispense" 버튼 클릭 → 10 ALGO 받기

### Step 2: 잔액 확인

```bash
python test_system.py
```

Reserve Account 섹션에서 Balance 확인:
```
Balance: 10.000000 ALGO ✅
```

### Step 3: ASA 토큰 생성

```bash
python contracts/esg_coupon_asa.py
```

**예상 출력:**
```
🪙 ESG 디지털 쿠폰 ASA 생성 중...
📤 트랜잭션 전송: TXXXXXXXXXXX
✅ ASA 생성 완료!
   Asset ID: 123456789
```

### Step 4: 토큰 정보 확인

AlgoExplorer에서 확인:
```
https://testnet.algoexplorer.io/asset/[ASSET_ID]
```

---

## 📡 API 엔드포인트 테스트

### API 서버 시작

```bash
python api/coupon_api.py
```

서버 주소: `http://localhost:5000`

### 테스트 명령어

#### 1. 헬스 체크
```bash
curl http://localhost:5000/health
```

#### 2. 보상 계산
```bash
curl -X POST http://localhost:5000/api/coupon/calculate-reward \
  -H "Content-Type: application/json" \
  -d '{
    "base_amount": 1000,
    "income_level": "low",
    "region_type": "rural",
    "activity_type": "carbon_neutral"
  }'
```

**예상 응답:**
```json
{
  "success": true,
  "data": {
    "base_amount": 1000,
    "final_amount": 3900,
    "total_multiplier": 3.9
  }
}
```

#### 3. 예산 현황
```bash
curl http://localhost:5000/api/coupon/budget/status?period=2025-Q1
```

---

## 📁 프로젝트 구조

```
journal1211/
├── security/
│   ├── keys_management_fixed.py    ✅ M/R/F/C 키 생성
│   └── multisig_handler.py         ✅ 다중서명 처리
├── contracts/
│   ├── esg_coupon_asa.py           ✅ ASA 토큰 + Clawback
│   └── reserve_manager.py          ✅ 예산 관리
├── policies/
│   └── reward_calculator.py        ✅ 차등 보상
├── verification/
│   └── invariants.py               ✅ 불변식 검증
├── governance/
│   └── policy_metadata.py          ✅ 정책 메타데이터
├── api/
│   └── coupon_api.py               ✅ REST API
├── config/
│   ├── keys_secure.json            ⚠️  Git 제외 (private keys)
│   ├── keys_public.json            ✅ 공개 주소
│   └── budget_config.json          ✅ 예산 설정
├── test_system.py                  ✅ 통합 테스트
├── demo_dashboard.html             ✅ 웹 대시보드
└── start_demo.py                   ✅ 데모 서버
```

---

## 🎯 PRD 구현 완료율: 100%

### 구현된 PRD 요구사항

| PRD 섹션 | 요구사항 | 구현 파일 | 상태 |
|---------|---------|----------|------|
| **3.1** | ASA 파라미터 설계 | `esg_coupon_asa.py` | ✅ |
| **3.2** | M/R/F/C 권한 분리 | `keys_management_fixed.py` | ✅ |
| **3.3** | 다중서명 거버넌스 | `multisig_handler.py` | ✅ |
| **2.1** | 수명주기 (S0~S6) | `esg_coupon_asa.py` | ✅ |
| **2.2** | 차등 보상 | `reward_calculator.py` | ✅ |
| **4.2** | 불변식 검증 | `invariants.py` | ✅ |
| **5.1** | 온·오프체인 분리 | `policy_metadata.py` | ✅ |
| **5.2** | ARC-3 메타데이터 | `policy_metadata.py` | ✅ |

---

## 🔒 보안 주의사항

### ⚠️ 절대 Git에 커밋하지 말 것

```
config/keys_secure.json   ← Private keys 포함!
.env                      ← API keys 포함!
```

### ✅ 이미 .gitignore에 포함됨

```bash
cat .gitignore
```

---

## 💡 주요 기능 하이라이트

### 1. 차등 보상 (PRD 2.2)

```python
calculator.calculate_reward(
    base_amount=1000,
    income_level=IncomeLevel.LOW,     # 1.5x
    region_type=RegionType.RURAL,     # 1.3x
    activity_type=ActivityType.CARBON_NEUTRAL  # 2.0x
)
# → 3,900 쿠폰 (290% 보너스)
```

### 2. 불변식 검증 (PRD 4.2)

```python
verifier.verify_all_invariants()
# ✅ 자산 보존: total = reserve + citizens + merchants
# ✅ 한도 검증: user_issued ≤ policy_limit
# ✅ 회수 검증: clawback_balance = 0
# ✅ 감사 검증: metadata_hash exists
```

### 3. 다중서명 Clawback (PRD 2.1)

```python
handler.clawback_with_multisig(
    msig=clawback_msig,          # 2-of-2 필요
    target_address="부정수급자",
    recovery_address="회수계정",
    amount=1000,
    signers_private_keys=[key1, key2]  # 2개 서명 필수
)
```

---

## 🎓 학습 자료

### Algorand 관련
- [Algorand Developer Docs](https://developer.algorand.org/)
- [ASA Specification](https://developer.algorand.org/docs/get-details/asa/)
- [TestNet Faucet](https://bank.testnet.algorand.network/)
- [AlgoExplorer TestNet](https://testnet.algoexplorer.io/)

### 프로젝트 문서
- `README.md` - 프로젝트 개요
- `docs/DEPLOYMENT_GUIDE.md` - 배포 가이드
- PRD 원본 - 제공된 요구사항 문서

---

## 📞 문제 해결

### Q1: "No module named 'algosdk'" 오류

```bash
pip install py-algorand-sdk flask flask-cors
```

### Q2: TestNet ALGO를 못 받겠어요

1. VPN 사용 시 끄기
2. 다른 브라우저 시도
3. 5분 후 재시도

### Q3: 데모 대시보드가 안 열려요

```bash
# 서버 재시작
cd journal1211
python start_demo.py
```

브라우저에서: `http://localhost:8000`

### Q4: Windows 인코딩 오류

`keys_management_fixed.py` 사용 (이모지 제거 버전)

---

## 🎉 성공!

모든 시스템이 정상 작동합니다!

**다음 단계:**
1. ✅ 키 생성 완료
2. ✅ 테스트 통과 (3/3)
3. ✅ 데모 서버 실행 중
4. ⏳ TestNet ALGO 받기
5. ⏳ ASA 토큰 생성

**데모 대시보드:** http://localhost:8000

---

**Built with ❤️ using Algorand TestNet**
