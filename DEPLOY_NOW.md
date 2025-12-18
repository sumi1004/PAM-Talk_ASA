# 🚀 지금 바로 배포하기 - 간단 가이드

## ⚡ 빠른 배포 (15분)

### 1단계: GitHub 저장소 생성 (5분)

#### 1-1. GitHub에서 새 저장소 만들기

**브라우저에서 https://github.com/new 접속**

```
Repository name: pam-talk-digital-coupon
Description: PAM-Talk 디지털 쿠폰 시스템 (Algorand ASA 기반)
☑️ Public
☐ Add a README file
☐ Add .gitignore
License: MIT License
```

"Create repository" 클릭

#### 1-2. 로컬에서 Git 초기화

```bash
cd D:\sumiWork\2025\journal\journal1211

# Git 초기화
git init

# GitHub 저장소 연결 (본인의 username으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/pam-talk-digital-coupon.git

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: PAM-Talk Digital Coupon System"

# 푸시
git branch -M main
git push -u origin main
```

**⚠️ 주의: YOUR_USERNAME을 본인의 GitHub username으로 변경하세요!**

---

### 2단계: Vercel 배포 (5분)

#### 2-1. Vercel 계정 생성/로그인

**브라우저에서 https://vercel.com 접속**

1. "Sign Up" 클릭
2. "Continue with GitHub" 선택
3. GitHub 계정으로 로그인

#### 2-2. 프로젝트 Import

**Vercel 대시보드에서:**

1. "Add New..." → "Project" 클릭
2. "Import Git Repository" 섹션에서:
   - `pam-talk-digital-coupon` 검색
   - "Import" 클릭

#### 2-3. 프로젝트 설정

**Configure Project 화면:**

```
Project Name: pam-talk-digital-coupon
Framework Preset: Other
Root Directory: ./

Build Command: (비워두기)
Output Directory: (비워두기)
Install Command: (비워두기)
```

#### 2-4. 환경 변수 설정 (선택)

**Environment Variables:**

```
ALGORAND_NETWORK = testnet
DEMO_MODE = true
```

#### 2-5. 배포!

"Deploy" 버튼 클릭 → 2-3분 대기

---

### 3단계: 배포 완료 확인 (2분)

#### 3-1. 배포 성공 메시지 확인

```
✓ Deployment ready

Your project is now live at:
https://pam-talk-digital-coupon.vercel.app
```

#### 3-2. 사이트 접속

**브라우저에서 열기:**
```
https://pam-talk-digital-coupon-YOUR_USERNAME.vercel.app
```

#### 3-3. 동작 확인

- ✅ 데모 대시보드 로딩
- ✅ M/R/F/C 키 정보 표시
- ✅ 차등 보상 시뮬레이터
- ✅ 예산 현황

---

### 4단계: README 업데이트 (3분)

#### 4-1. README.md에 배포 URL 추가

```bash
# README.md 열기
notepad README.md
```

**파일 상단에 추가:**
```markdown
## 🌐 Live Demo

**배포 사이트:** https://pam-talk-digital-coupon.vercel.app

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/pam-talk-digital-coupon)
```

#### 4-2. 변경사항 푸시

```bash
git add README.md
git commit -m "Add live demo URL to README"
git push
```

---

## ✅ 배포 완료 체크리스트

- [ ] GitHub 저장소 생성 완료
- [ ] Git push 완료
- [ ] Vercel 계정 생성 완료
- [ ] 프로젝트 Import 완료
- [ ] 배포 성공 확인
- [ ] 사이트 접속 가능
- [ ] README에 URL 추가
- [ ] 공유 준비 완료!

---

## 🎉 성공!

**이제 전 세계 누구나 접속 가능합니다:**

```
https://pam-talk-digital-coupon.vercel.app
```

**공유하기:**
- 📧 이메일로 전송
- 💬 SNS에 포스팅
- 📱 QR 코드 생성
- 📝 포트폴리오에 추가

---

## 🔄 업데이트 방법 (자동 배포)

**코드 수정 후:**

```bash
git add .
git commit -m "Update: 기능 개선"
git push
```

→ Vercel이 자동으로 재배포! (1-2분)

---

## 📊 사용 통계 확인

**Vercel 대시보드에서:**

```
Analytics → View
- 페이지 뷰
- 방문자 수
- 지역별 접속
```

---

## 🛠️ 문제 해결

### Q: 배포 실패

**A: Vercel 로그 확인**
```
Vercel Dashboard → Deployments → (실패한 배포) → View Function Logs
```

### Q: 사이트가 안 열림

**A: 몇 분 더 기다리기**
- 첫 배포는 5-10분 소요 가능
- 캐시 갱신 대기

### Q: 키 정보가 안 보임

**A: config/keys_public.json 확인**
```bash
# 파일이 있는지 확인
ls config/keys_public.json

# Git에 포함되었는지 확인
git ls-files | grep keys_public.json
```

---

## 📞 도움이 필요하면

1. `VERCEL_DEPLOYMENT_PROCESS.md` 상세 가이드 참조
2. GitHub Issues에 질문 올리기
3. Vercel Discord 참여: https://vercel.com/discord

---

**지금 바로 배포하세요!** 🚀

```bash
# 한 번에 실행
git init
git remote add origin https://github.com/YOUR_USERNAME/pam-talk-digital-coupon.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

그 다음 https://vercel.com 에서 Import!
