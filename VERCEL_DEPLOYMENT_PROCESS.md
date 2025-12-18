# PAM-Talk 디지털 쿠폰 시스템 - Vercel 배포 프로세스

## 📋 배포 전체 프로세스 (30분)

### Phase 1: GitHub 저장소 준비 (10분)
### Phase 2: Vercel 배포 설정 (10분)
### Phase 3: 환경 변수 설정 (5분)
### Phase 4: 배포 및 테스트 (5분)

---

## Phase 1: GitHub 저장소 준비

### Step 1-1: Git 저장소 초기화

```bash
cd D:\sumiWork\2025\journal\journal1211

# Git 초기화
git init

# .gitignore 확인 (이미 있음)
cat .gitignore
```

**중요: .gitignore 내용 확인**
```bash
# 다음 파일들이 포함되어 있어야 함
config/keys_secure.json
.env
*.pem
*.key
```

### Step 1-2: 민감 정보 제거 확인

```bash
# 민감 정보가 포함되지 않았는지 확인
git status

# 다음이 표시되면 안 됨:
# config/keys_secure.json
# .env
```

### Step 1-3: GitHub 저장소 생성

**웹 브라우저에서:**
1. https://github.com 접속
2. 오른쪽 상단 "+" → "New repository" 클릭
3. 저장소 정보 입력:
   ```
   Repository name: pam-talk-digital-coupon
   Description: PAM-Talk 디지털 쿠폰 시스템 (Algorand 기반)
   Public/Private: Public 선택
   ✅ Add a README file: 체크 해제 (이미 있음)
   ✅ Add .gitignore: None (이미 있음)
   ✅ Choose a license: MIT License
   ```
4. "Create repository" 클릭

### Step 1-4: 로컬 저장소와 연결

```bash
# GitHub 저장소 URL 복사 (예: https://github.com/YOUR_USERNAME/pam-talk-digital-coupon.git)

# 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/pam-talk-digital-coupon.git

# 초기 커밋
git add .
git commit -m "Initial commit: PAM-Talk Digital Coupon System

- M/R/F/C key management
- ASA token with Clawback
- Differential reward calculator
- Reserve budget manager
- Invariants verification
- Multi-signature governance
- Policy metadata with hash anchoring
- REST API (9 endpoints)
- Demo dashboard
- Complete documentation (4 guides)
"

# 푸시
git branch -M main
git push -u origin main
```

**⚠️ 주의: 푸시 전 마지막 확인**
```bash
# 민감 정보가 없는지 재확인
git log --stat | grep -i "keys_secure\|\.env"

# 아무것도 나오지 않아야 함!
```

---

## Phase 2: Vercel 배포 설정

### Step 2-1: Vercel 계정 생성/로그인

**웹 브라우저에서:**
1. https://vercel.com 접속
2. "Sign Up" 또는 "Login" 클릭
3. "Continue with GitHub" 선택
4. GitHub 계정으로 로그인 허용

### Step 2-2: 프로젝트 생성 파일 준비

**journal1211 폴더에 Vercel 설정 파일 생성:**

#### `vercel.json` 생성
```bash
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "api/coupon_api.py",
      "use": "@vercel/python"
    },
    {
      "src": "demo_dashboard.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/",
      "dest": "/demo_dashboard.html"
    },
    {
      "src": "/api/(.*)",
      "dest": "api/coupon_api.py"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
EOF
```

#### `requirements.txt` 최종 확인
```bash
cat requirements.txt
```

**내용:**
```
py-algorand-sdk==2.6.0
flask==3.0.0
flask-cors==4.0.0
pycryptodome==3.19.0
cryptography==41.0.7
sqlalchemy==2.0.23
python-dotenv==1.0.0
pyyaml==6.0.1
jsonschema==4.20.0
```

#### `api/index.py` 생성 (Vercel 진입점)
```bash
cat > api/index.py << 'EOF'
from coupon_api import app

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)
EOF
```

### Step 2-3: API 경로 수정 (Serverless 호환)

**`api/coupon_api.py` 수정:**

```python
# 파일 상단에 추가
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

**상대 경로를 절대 경로로 변경:**

```python
# Before
from contracts.reserve_manager import ReserveManager

# After (이미 되어있음)
sys.path.append("..")
from contracts.reserve_manager import ReserveManager
```

### Step 2-4: 정적 파일 경로 설정

**`demo_dashboard.html` 수정:**

```html
<!-- Before -->
<script>
fetch('config/keys_public.json')

<!-- After -->
<script>
fetch('/config/keys_public.json')
```

### Step 2-5: 변경 사항 커밋

```bash
git add vercel.json api/index.py
git commit -m "Add Vercel deployment configuration"
git push
```

---

## Phase 3: Vercel에서 프로젝트 배포

### Step 3-1: Vercel에서 프로젝트 Import

**Vercel 대시보드에서:**
1. "Add New..." → "Project" 클릭
2. "Import Git Repository" 섹션에서 GitHub 연동
3. 저장소 검색: `pam-talk-digital-coupon`
4. "Import" 클릭

### Step 3-2: 프로젝트 설정

**Configure Project 화면에서:**

```
Project Name: pam-talk-digital-coupon
Framework Preset: Other
Root Directory: ./
```

**Build Settings:**
```
Build Command: (비워두기 - 정적 사이트이므로)
Output Directory: (비워두기)
Install Command: pip install -r requirements.txt
```

### Step 3-3: 환경 변수 설정

**Environment Variables 섹션:**

⚠️ **중요: 실제 키는 절대 공개하지 마세요!**

```
ALGORAND_NETWORK=testnet
ALGORAND_ALGOD_ADDRESS=https://testnet-api.algonode.cloud
ALGORAND_ALGOD_TOKEN=

# 테스트용 (실제 키는 사용하지 마세요)
DEMO_MODE=true
```

### Step 3-4: 배포 시작

1. "Deploy" 버튼 클릭
2. 배포 진행 상황 확인 (약 2-3분)

**배포 로그 예시:**
```
Installing dependencies...
✓ py-algorand-sdk installed
✓ flask installed
Building...
✓ Build completed
Deploying...
✓ Deployment ready
```

### Step 3-5: 배포 완료 확인

**배포 성공 시:**
```
✓ Deployment ready

Your deployment is now live at:
https://pam-talk-digital-coupon.vercel.app
```

---

## Phase 4: 배포 후 설정 및 테스트

### Step 4-1: 커스텀 도메인 설정 (선택)

**Vercel 프로젝트 설정에서:**
1. "Settings" → "Domains"
2. "Add" 클릭
3. 도메인 입력 (예: `pamtalk-coupon.com`)
4. DNS 설정 따라하기

**무료 Vercel 도메인:**
```
https://pam-talk-digital-coupon.vercel.app
https://pam-talk-digital-coupon-{username}.vercel.app
```

### Step 4-2: 사이트 접속 테스트

**웹 브라우저에서:**
```
https://pam-talk-digital-coupon.vercel.app
```

**확인 사항:**
- ✅ 데모 대시보드 로딩
- ✅ M/R/F/C 키 정보 표시 (공개 주소만)
- ✅ 차등 보상 시뮬레이터 동작
- ✅ 예산 현황 표시

### Step 4-3: API 엔드포인트 테스트

```bash
# 헬스 체크
curl https://pam-talk-digital-coupon.vercel.app/api/health

# 보상 계산
curl -X POST https://pam-talk-digital-coupon.vercel.app/api/coupon/calculate-reward \
  -H "Content-Type: application/json" \
  -d '{"base_amount":1000,"income_level":"low","region_type":"rural","activity_type":"carbon_neutral"}'
```

**예상 응답:**
```json
{
  "success": true,
  "data": {
    "final_amount": 3900,
    "total_multiplier": 3.9
  }
}
```

### Step 4-4: 문제 해결 (배포 실패 시)

#### 문제 1: Python 모듈 오류
```
ModuleNotFoundError: No module named 'algosdk'
```

**해결:**
```bash
# requirements.txt 확인
cat requirements.txt

# 버전 명시
py-algorand-sdk==2.6.0
```

#### 문제 2: 경로 오류
```
FileNotFoundError: config/keys_public.json
```

**해결:**
```python
# 절대 경로 사용
import os
BASE_DIR = os.path.dirname(__file__)
config_path = os.path.join(BASE_DIR, '../config/keys_public.json')
```

#### 문제 3: Serverless 타임아웃
```
Function execution timed out after 10s
```

**해결:**
```json
// vercel.json에 추가
{
  "functions": {
    "api/coupon_api.py": {
      "maxDuration": 30
    }
  }
}
```

---

## Phase 5: 지속적 배포 (CI/CD) 설정

### Step 5-1: 자동 배포 활성화

**Vercel은 GitHub 연동 시 자동으로 CI/CD 활성화됨:**

```
main 브랜치 push → 자동 배포
Pull Request 생성 → 프리뷰 배포
```

### Step 5-2: 브랜치 전략

```bash
# 개발 브랜치 생성
git checkout -b develop
git push -u origin develop
```

**Vercel 설정:**
- `main` → Production 배포
- `develop` → Preview 배포
- Pull Request → Preview 배포

### Step 5-3: 배포 알림 설정

**Vercel 프로젝트 설정:**
1. "Settings" → "Notifications"
2. 이메일 또는 Slack 연동
3. 배포 성공/실패 알림 활성화

---

## Phase 6: 모니터링 및 분석

### Step 6-1: Vercel Analytics 활성화

**Vercel 대시보드:**
1. 프로젝트 선택
2. "Analytics" 탭
3. "Enable Analytics" 클릭

**무료 플랜 제공:**
- 페이지 뷰
- 방문자 수
- 지역별 접속
- 성능 메트릭

### Step 6-2: 로그 확인

**실시간 로그:**
```
Vercel Dashboard → Project → Deployments → (최신 배포) → View Function Logs
```

**로그 예시:**
```
[GET] /api/health - 200 OK (45ms)
[POST] /api/coupon/calculate-reward - 200 OK (120ms)
[GET] /config/keys_public.json - 200 OK (15ms)
```

### Step 6-3: 성능 모니터링

**Vercel Speed Insights:**
1. "Settings" → "Speed Insights"
2. "Enable Speed Insights" 클릭

**측정 항목:**
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)

---

## 📋 배포 체크리스트

### 배포 전 확인

- [ ] `.gitignore`에 민감 정보 포함 확인
- [ ] `keys_secure.json` Git에서 제외 확인
- [ ] `.env` 파일 Git에서 제외 확인
- [ ] `requirements.txt` 버전 명시
- [ ] `vercel.json` 설정 완료
- [ ] 상대 경로 → 절대 경로 변경
- [ ] API 엔드포인트 테스트 (로컬)

### 배포 후 확인

- [ ] 웹사이트 접속 확인
- [ ] 데모 대시보드 로딩
- [ ] API 헬스 체크 성공
- [ ] 공개 키 정보 표시
- [ ] 보상 계산 API 동작
- [ ] 모바일 반응형 확인
- [ ] HTTPS 적용 확인

### 보안 확인

- [ ] Private key 노출 없음
- [ ] .env 파일 제외됨
- [ ] HTTPS 강제 적용
- [ ] CORS 설정 확인
- [ ] Rate Limiting 고려

---

## 🌐 배포 완료 URL

### 예상 URL 구조

```
메인 사이트:
https://pam-talk-digital-coupon.vercel.app

API 엔드포인트:
https://pam-talk-digital-coupon.vercel.app/api/health
https://pam-talk-digital-coupon.vercel.app/api/coupon/info
https://pam-talk-digital-coupon.vercel.app/api/coupon/calculate-reward

문서:
https://pam-talk-digital-coupon.vercel.app/USER_MANUAL.md
https://pam-talk-digital-coupon.vercel.app/QUICK_REFERENCE.md
```

---

## 🔧 고급 설정 (선택)

### 커스텀 404 페이지

**`404.html` 생성:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>404 - Page Not Found</title>
</head>
<body>
    <h1>404 - Page Not Found</h1>
    <p><a href="/">Go to Home</a></p>
</body>
</html>
```

### 리다이렉트 설정

**`vercel.json`에 추가:**
```json
{
  "redirects": [
    {
      "source": "/docs",
      "destination": "/USER_MANUAL.md"
    },
    {
      "source": "/guide",
      "destination": "/QUICK_REFERENCE.md"
    }
  ]
}
```

### 환경별 설정

**Production vs Preview:**
```json
{
  "env": {
    "ALGORAND_NETWORK": "mainnet"
  },
  "build": {
    "env": {
      "ALGORAND_NETWORK": "testnet"
    }
  }
}
```

---

## 📊 예상 비용

### Vercel 무료 플랜

```
✅ 무제한 배포
✅ 100GB 대역폭/월
✅ Serverless Functions (10초 실행 제한)
✅ 자동 HTTPS
✅ GitHub 연동
✅ 프리뷰 배포
```

**충분한 경우:**
- 데모 사이트
- 소규모 프로젝트
- 개인 포트폴리오

**유료 전환 필요한 경우:**
- 대역폭 100GB 초과
- 함수 실행 시간 10초 초과
- 팀 협업 기능 필요

---

## 🎓 학습 자료

### Vercel 공식 문서
- https://vercel.com/docs
- https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python

### Python on Vercel
- https://vercel.com/docs/frameworks/python

### 예제 프로젝트
- https://github.com/vercel/examples

---

## 📞 문제 발생 시

### Vercel 지원
- 📧 Discord: https://vercel.com/discord
- 📚 Documentation: https://vercel.com/docs
- 🐛 GitHub Issues: https://github.com/vercel/vercel/issues

### 커뮤니티
- Stack Overflow: `[vercel]` 태그
- Reddit: r/vercel

---

## ✅ 최종 확인

배포 완료 후 다음을 확인하세요:

```bash
# 1. 사이트 접속
open https://pam-talk-digital-coupon.vercel.app

# 2. API 테스트
curl https://pam-talk-digital-coupon.vercel.app/api/health

# 3. GitHub 저장소 확인
open https://github.com/YOUR_USERNAME/pam-talk-digital-coupon

# 4. Vercel 대시보드 확인
open https://vercel.com/dashboard
```

---

## 🎉 배포 완료!

**축하합니다! PAM-Talk 디지털 쿠폰 시스템이 전 세계에 공개되었습니다!**

**공유 가능한 URL:**
```
https://pam-talk-digital-coupon.vercel.app
```

**다음 단계:**
1. README.md에 배포 URL 추가
2. 소셜 미디어에 공유
3. 포트폴리오에 추가
4. 피드백 수집 및 개선

---

**⚠️ 중요 알림**

배포 전 반드시:
1. `config/keys_secure.json` Git에서 제외 확인
2. `.env` 파일 제외 확인
3. 테스트용 키만 사용 (실제 키 절대 금지!)
4. TestNet만 사용 (MainNet 금지!)
