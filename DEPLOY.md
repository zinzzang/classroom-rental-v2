# 📦 배포 가이드

강의실 대여 시스템을 배포하는 여러 방법을 소개합니다.

---

## 🏠 옵션 1: 로컬 네트워크에서 사용 (가장 간단)

**같은 Wi-Fi를 사용하는 사람들이 접근할 수 있습니다.**

### 1단계: 서버 실행
```bash
cd /Users/adorable/classroom_rental/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2단계: 내 IP 주소 확인
```bash
# Mac/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# 예시 출력: inet 192.168.0.10
```

### 3단계: 다른 사람들에게 알려주기
- 사용자 페이지: `http://192.168.0.10:8000/`
- 관리자 페이지: `http://192.168.0.10:8000/admin`

### ⚠️ 주의사항:
- 서버를 실행한 컴퓨터가 켜져 있어야 함
- 같은 네트워크(Wi-Fi)에 연결되어 있어야 함
- 방화벽이 8000 포트를 허용해야 함

---

## ☁️ 옵션 2: Render.com 무료 배포 (추천!)

**인터넷 어디서든 접근 가능, 무료, 설정 쉬움**

### 준비사항:
1. GitHub 계정 생성
2. Render.com 계정 생성 (무료)

### 배포 순서:

#### 1. GitHub에 코드 업로드
```bash
cd /Users/adorable/classroom_rental
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/classroom_rental.git
git push -u origin main
```

#### 2. Render.com에서 배포
1. https://render.com 접속 → 로그인
2. "New +" → "Web Service" 클릭
3. GitHub 연동 후 저장소 선택
4. 설정:
   - **Name**: classroom-rental
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. "Create Web Service" 클릭

#### 3. 배포 완료!
- URL: `https://classroom-rental-xxxx.onrender.com`
- 무료 플랜은 15분 미사용 시 슬립 모드 (첫 접속 시 느림)

---

## 🐳 옵션 3: Docker 배포

**전문적인 배포, 어디서든 실행 가능**

### 사용:
```bash
cd /Users/adorable/classroom_rental

# 빌드
docker-compose build

# 실행
docker-compose up -d

# 중지
docker-compose down
```

접속: http://localhost:8000

---

## 🚂 옵션 4: Railway.app 배포

**간단한 클라우드 배포, 무료 크레딧 제공**

1. https://railway.app 접속
2. "Start a New Project" → "Deploy from GitHub"
3. 저장소 연결
4. 자동 배포 완료!

---

## 🔧 배포 후 설정

### HTML의 API 주소 변경

배포 후 `frontend/admin.html`과 `frontend/user.html`의 API_BASE를 수정하세요:

```javascript
// 로컬
const API_BASE = "http://127.0.0.1:8000";

// 배포 후 (예시)
const API_BASE = "https://classroom-rental-xxxx.onrender.com";
```

또는 환경에 따라 자동 설정:
```javascript
const API_BASE = window.location.origin;
```

---

## 📊 비교표

| 방법 | 난이도 | 비용 | 접근성 | 추천 대상 |
|------|--------|------|--------|-----------|
| 로컬 네트워크 | ⭐ | 무료 | 같은 Wi-Fi만 | 개인/테스트 |
| Render.com | ⭐⭐ | 무료 | 전세계 | 소규모 운영 |
| Docker | ⭐⭐⭐ | VPS 비용 | 전세계 | 중대규모 |
| Railway | ⭐⭐ | 일부 무료 | 전세계 | 소규모 운영 |

---

## ❓ 추천

- **빠른 테스트**: 로컬 네트워크
- **실제 사용**: Render.com (무료)
- **대규모 사용**: Docker + AWS/GCP

어떤 방법이 필요하신가요?

