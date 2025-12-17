# 🔧 Render 배포 오류 해결

## ❌ 오류 메시지
```
Root directory "backend" does not exist.
```

## ✅ 해결 방법

### 방법 1: Root Directory 제거 (가장 쉬움!)

Render.com 설정을 다음과 같이 변경하세요:

#### 현재 설정 (잘못됨):
```
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 올바른 설정:
```
Root Directory: (비워두기 - 삭제!)
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 📝 단계별 수정 방법:

1. **Render.com 대시보드 접속**
   - https://dashboard.render.com

2. **서비스 선택**
   - `classroom-rental` 서비스 클릭

3. **Settings 탭 클릭**

4. **설정 수정:**

   **Root Directory:**
   - 현재: `backend`
   - 변경: **(완전히 비워두기)**

   **Build Command:**
   - 현재: `pip install -r requirements.txt`
   - 변경: `cd backend && pip install -r requirements.txt`

   **Start Command:**
   - 현재: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - 변경: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Save Changes 클릭**

6. **자동으로 재배포 시작!**

---

## 방법 2: GitHub 파일 확인

혹시 GitHub에 파일이 제대로 올라가지 않았다면:

### 1. GitHub 저장소 확인
https://github.com/zinzzang/classroom-rental

다음 구조가 보여야 합니다:
```
classroom-rental/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── cleanup_db.py
├── frontend/
│   ├── admin.html
│   └── user.html
├── README.md
└── ...
```

### 2. 파일이 없다면 다시 푸시

터미널에서:

```bash
cd /Users/adorable/classroom_rental

# 현재 상태 확인
git status

# 모든 파일 추가
git add .
git add backend/
git add frontend/

# 커밋
git commit -m "Fix: Add all files"

# 푸시 (Personal Access Token 필요)
git push origin master
```

#### Personal Access Token 만들기:
1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. 권한: `repo` 체크
5. Generate token
6. 토큰 복사

#### 푸시 시 인증:
```bash
git push origin master

# Username: zinzzang
# Password: (복사한 토큰 붙여넣기)
```

---

## 방법 3: 새로 배포하기

문제가 계속되면 서비스를 삭제하고 다시 만드세요:

1. Render 대시보드 → 서비스 선택
2. Settings → Delete Service
3. 다시 "New +" → "Web Service"
4. 올바른 설정으로 생성:
   ```
   Root Directory: (비워두기!)
   Build: cd backend && pip install -r requirements.txt
   Start: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

---

## 🎯 권장 해결 순서

1. ✅ **방법 1 시도** (가장 빠름, 5분)
2. ❌ 안 되면 → GitHub 확인
3. ❌ 여전히 안 되면 → 방법 3 (새로 배포)

---

## 📸 스크린샷 가이드

### Render Settings 화면:

```
┌─────────────────────────────────────┐
│ Build & Deploy                       │
├─────────────────────────────────────┤
│ Root Directory                       │
│ [                              ]     │  ← 비워두기!
│                                      │
│ Build Command                        │
│ [cd backend && pip install -r req...]│
│                                      │
│ Start Command                        │
│ [cd backend && uvicorn main:app ...] │
│                                      │
│ [Save Changes]                       │
└─────────────────────────────────────┘
```

---

## ✅ 성공 확인

배포가 성공하면 로그에 다음과 같이 표시됩니다:

```
==> Cloning from https://github.com/zinzzang/classroom-rental
==> Checking out commit 386033e
==> Running build command 'cd backend && pip install -r requirements.txt'
    Collecting fastapi
    Collecting uvicorn
    ...
    Successfully installed ...
==> Uploading build...
==> Starting service with 'cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT'
    INFO:     Started server process
    INFO:     Uvicorn running on http://0.0.0.0:10000
    INFO:     Application startup complete.
```

---

## 🆘 여전히 안 되나요?

다음 정보를 확인하세요:

1. **GitHub 저장소 URL:**
   https://github.com/zinzzang/classroom-rental

2. **backend/ 폴더가 보이나요?**
   - 보임 ✅ → Render 설정 문제
   - 안 보임 ❌ → GitHub 푸시 문제

3. **Render 로그 확인:**
   - Render 대시보드 → Logs 탭
   - 빨간색 에러 메시지 확인

**도움이 필요하면 Render 로그 전체를 복사해서 보내주세요!**

