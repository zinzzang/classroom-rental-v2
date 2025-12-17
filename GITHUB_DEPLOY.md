# 🚀 GitHub + Render.com 무료 배포 가이드

## 📋 준비물
- GitHub 계정 (없으면 https://github.com 에서 가입)
- Render.com 계정 (없으면 https://render.com 에서 가입)

---

## 1️⃣ GitHub에 코드 업로드

### 1-1. GitHub 저장소 생성

1. https://github.com 접속 → 로그인
2. 우측 상단 "+" → "New repository" 클릭
3. 설정:
   - Repository name: `classroom-rental`
   - Public 선택 (무료 배포는 Public만 가능)
   - "Create repository" 클릭

### 1-2. 로컬 코드를 GitHub에 푸시

터미널에서 실행:

```bash
cd /Users/adorable/classroom_rental

# Git 초기화 (이미 했다면 생략)
git init

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: 강의실 대여 시스템"

# GitHub 저장소 연결 (YOUR_USERNAME을 본인 GitHub 아이디로 변경!)
git remote add origin https://github.com/YOUR_USERNAME/classroom-rental.git

# 푸시
git branch -M main
git push -u origin main
```

**⚠️ 에러가 나면:**
```bash
# GitHub 인증 설정
git config --global user.name "본인이름"
git config --global user.email "본인이메일@example.com"

# Personal Access Token 필요 시:
# GitHub → Settings → Developer settings → Personal access tokens
# → Generate new token (classic) → repo 권한 체크
```

---

## 2️⃣ Render.com에서 배포

### 2-1. Render.com 가입 및 연동

1. https://render.com 접속
2. "Get Started for Free" 클릭
3. GitHub 계정으로 로그인 (연동)

### 2-2. Web Service 생성

1. 대시보드에서 "New +" 버튼 클릭
2. "Web Service" 선택
3. GitHub 저장소 연결:
   - "Connect a repository" 클릭
   - `classroom-rental` 저장소 선택
   - "Connect" 클릭

### 2-3. 배포 설정

다음과 같이 입력:

| 항목 | 값 |
|------|-----|
| **Name** | `classroom-rental` (또는 원하는 이름) |
| **Region** | Singapore (가장 가까운 지역) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

**Environment Variables (환경 변수):**

"Add Environment Variable" 클릭하여 추가:

```
JWT_SECRET = your-super-secret-key-change-this-12345
DEFAULT_ADMIN_USERNAME = admin
DEFAULT_ADMIN_PASSWORD = admin1234
```

### 2-4. 배포 시작!

1. "Create Web Service" 버튼 클릭
2. 배포 시작 (5~10분 소요)
3. 로그를 보면서 진행 상황 확인

---

## 3️⃣ 배포 완료! 🎉

### 접속 주소

배포가 완료되면 URL이 생성됩니다:

```
https://classroom-rental-xxxx.onrender.com
```

- **사용자 페이지**: https://classroom-rental-xxxx.onrender.com/
- **관리자 페이지**: https://classroom-rental-xxxx.onrender.com/admin
- **API 문서**: https://classroom-rental-xxxx.onrender.com/docs

### ✅ 확인사항

1. 사용자 페이지 접속 → 강의실 목록 보이는지 확인
2. 관리자 페이지 접속 → 로그인 (admin / admin1234)
3. 정상 작동 확인!

---

## 🔄 코드 수정 후 재배포

코드를 수정한 후:

```bash
cd /Users/adorable/classroom_rental

git add .
git commit -m "수정 내용 설명"
git push
```

→ Render.com이 **자동으로 재배포**합니다! (5분 소요)

---

## 💾 데이터베이스 관리

### 무료 플랜의 제약:
- SQLite 파일이 서버에 저장됨
- **재배포 시 데이터가 초기화될 수 있음**

### 해결 방법:

#### 옵션 1: PostgreSQL 사용 (추천)

Render.com에서 무료 PostgreSQL 제공:

1. Render 대시보드 → "New +" → "PostgreSQL"
2. 무료 플랜 선택
3. 생성된 "Internal Database URL" 복사
4. Web Service의 Environment Variables에 추가:
   ```
   DB_URL = postgresql://user:pass@host/db
   ```

#### 옵션 2: 정기적으로 오래된 데이터 삭제

관리자 페이지에서 통계 확인:
- API: `GET /admin/stats`
- 6개월 이전 일정 자동 삭제: `DELETE /admin/schedules/cleanup/old`

---

## 🐛 문제 해결

### 배포 실패 시

**로그 확인:**
- Render 대시보드 → Logs 탭 확인

**흔한 오류:**

1. **Module not found**
   → `requirements.txt`에 패키지 추가 확인

2. **Port binding failed**
   → Start Command가 `--port $PORT` 포함하는지 확인

3. **Database error**
   → 환경 변수 확인

### 슬립 모드 방지

무료 플랜은 15분 미사용 시 슬립 모드 진입.

**해결 방법:**
1. **UptimeRobot** 사용 (무료):
   - https://uptimerobot.com
   - 5분마다 자동으로 사이트 핑
   - 슬립 모드 방지

2. **유료 플랜** 업그레이드 ($7/월):
   - 슬립 모드 없음
   - 더 빠른 성능

---

## 📊 무료 vs 유료 비교

| 기능 | 무료 | 유료 ($7/월) |
|------|------|--------------|
| 배포 | ✅ | ✅ |
| 커스텀 도메인 | ❌ | ✅ |
| 슬립 모드 | 15분 후 | ❌ 없음 |
| 메모리 | 512MB | 1GB+ |
| 데이터베이스 | 제한적 | PostgreSQL |

**소규모 사용에는 무료로 충분합니다!**

---

## 🎯 다음 단계

1. ✅ GitHub에 업로드
2. ✅ Render.com 배포
3. 🔐 관리자 비밀번호 변경
4. 📱 사용자들에게 URL 공유
5. 🎉 사용 시작!

**문제가 생기면 Render 로그를 확인하세요!**

