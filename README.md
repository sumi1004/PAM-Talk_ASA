# PAM-Talk 디지털 쿠폰 시스템 (ASA 기반)

## 🌐 Live Demo

**배포 사이트:** https://pam-talk-asa.vercel.app

[![GitHub](https://img.shields.io/badge/GitHub-sumi1004%2FPAM--Talk__ASA-blue?logo=github)](https://github.com/sumi1004/PAM-Talk_ASA)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-success?logo=vercel)](https://pam-talk-asa.vercel.app)
[![Algorand](https://img.shields.io/badge/Algorand-TestNet-00D1B2?logo=algorand)](https://testnet.algoexplorer.io/)

### Quick Access
- 📊 **Dashboard**: [https://pam-talk-asa.vercel.app](https://pam-talk-asa.vercel.app)
- 📖 **User Manual**: [USER_MANUAL.md](USER_MANUAL.md)
- ⚡ **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- 🧪 **TestNet Guide**: [TESTNET_DEMO_GUIDE.md](TESTNET_DEMO_GUIDE.md)
- 🚀 **Deploy Guide**: [VERCEL_DEPLOYMENT_PROCESS.md](VERCEL_DEPLOYMENT_PROCESS.md)

---

## 프로젝트 개요

PAM-Talk 기반 디지털 쿠폰 시스템은 Algorand ASA를 활용하여 시민참여형 ESG 보상정책을 구현합니다.

### 핵심 기능

- **M/R/F/C 권한 분리**: Manager, Reserve, Freeze, Clawback 키 분리
- **다중서명 거버넌스**: 2-of-3, 2-of-2 다중서명 지원
- **Clawback 회수**: 부정수급 자동 회수 시스템
- **불변식 검증**: 자산 보존, 한도 검증 자동화
- **MRV 구조**: 측정·보고·검증 온체인 기록
- **차등 보상**: 소득·지역·행동유형별 보상 차등화

## 디렉토리 구조

```
journal1211/
├── security/           # 키 관리 및 보안
│   ├── keys_management.py
│   ├── multisig_handler.py
│   └── hsm_integration.py
├── contracts/          # 스마트 계약
│   ├── esg_coupon_asa.py
│   ├── reserve_manager.py
│   └── clawback_handler.py
├── governance/         # 거버넌스 및 감사
│   ├── policy_metadata.py
│   ├── audit_logger.py
│   └── committee_vote.py
├── policies/           # 정책 집행
│   ├── budget_manager.py
│   ├── limit_enforcer.py
│   └── reward_calculator.py
├── verification/       # 검증 시스템
│   ├── invariants.py
│   ├── mrv_verifier.py
│   └── compliance_checker.py
├── api/                # REST API
│   ├── coupon_api.py
│   └── admin_api.py
├── config/             # 설정 파일
│   └── asa_config.json
├── tests/              # 테스트
│   └── test_*.py
└── docs/               # 문서
    └── deployment_guide.md
```

## 빠른 시작

### 1. 환경 설정

```bash
cd journal1211
pip install -r requirements.txt
```

### 2. 키 생성 (최초 1회)

```bash
python security/keys_management.py --init
```

### 3. ASA 토큰 배포

```bash
python contracts/esg_coupon_asa.py --deploy --network testnet
```

### 4. API 서버 시작

```bash
python api/coupon_api.py
```

## 주요 특징

### 1. M/R/F/C 권한 분리

| 권한 | 역할 | 다중서명 |
|------|------|---------|
| Manager | 메타데이터 변경 | 2-of-3 |
| Reserve | 예산 배분 | 단일 (HSM) |
| Freeze | 계정 동결 | 2-of-3 |
| Clawback | 자산 회수 | 2-of-2 |

### 2. 불변식 검증

```python
# 자동으로 다음 항목 검증
1. total_supply = reserve + citizens + merchants + clawback
2. user_issued_amount <= policy_limit
3. clawback_account_balance = 0 (회수 후)
4. metadata_hash_count >= 1 (정책별)
```

### 3. 차등 보상

- 소득 3분위: 100%, 120%, 150%
- 지역 가중치: 도시권 100%, 농어촌 130%
- 행동유형: 기본~탄소중립 100%~200%

## 라이선스

MIT License
