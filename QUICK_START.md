# 🚀 빠른 시작 가이드

## 💤 "슬립 모드"란?

**무료 클라우드 배포의 특징:**
- 15분 동안 아무도 접속하지 않으면 → 서버가 **잠들어요** (절전 모드)
- 누군가 다시 접속하면 → **깨어나는데 30초~1분** 정도 걸림
- 깨어난 후에는 정상 속도로 작동
- **사용 중일 때는 계속 빠름!**

**비유:** 컴퓨터 절전 모드와 똑같아요. 첫 접속만 느리고, 이후는 빠릅니다.

---

## 🎯 무료 배포 3단계

### 1단계: GitHub에 업로드 (5분)

```bash
cd /Users/adorable/classroom_rental

# Git 초기화
git init
git add .
git commit -m "강의실 대여 시스템 v1.0"

# GitHub 저장소 생성 후 (github.com에서)
git remote add origin https://github.com/본인아이디/classroom-rental.git
git push -u origin main
```

### 2단계: Render.com 배포 (5분)

1. https://render.com 접속 → GitHub로 가입
2. "New +" → "Web Service"
3. 저장소 연결: `classroom-rental`
4. 설정 입력:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. "Create Web Service" 클릭

### 3단계: 완료! (자동)

5~10분 후 배포 완료:
- **URL**: https://classroom-rental-xxxx.onrender.com
- 전세계 어디서나 접속 가능!

---

## 💾 데이터베이스 관리

### ❓ "DB가 너무 많아지면 삭제해야 하나요?"

**네, 정기적으로 관리하는 게 좋습니다!**

### 자동 정리 기능 추가됨 ✅

**관리자 페이지에서:**
1. "통계/관리" 탭 클릭
2. 시스템 통계 확인
3. "6개월 이전 일정 삭제" 버튼 클릭

**또는 API로:**
```bash
# 통계 확인
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-app.onrender.com/admin/stats

# 6개월 이전 일정 삭제
curl -X DELETE -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-app.onrender.com/admin/schedules/cleanup/old
```

**또는 스크립트로:**
```bash
cd backend
python cleanup_db.py
```

### 권장 관리 주기

| 사용량 | 정리 주기 | 보관 기간 |
|--------|-----------|-----------|
| 소규모 | 6개월마다 | 6개월 |
| 중규모 | 3개월마다 | 3개월 |
| 대규모 | 1개월마다 | 1개월 |

---

## 🔐 보안 설정

**배포 후 반드시 변경하세요!**

Render.com → Environment Variables:

```
JWT_SECRET = 강력한-랜덤-시크릿-키-12345
DEFAULT_ADMIN_PASSWORD = 새로운비밀번호
```

---

## 📊 무료 vs 유료

| 항목 | 무료 | 유료 ($7/월) |
|------|------|--------------|
| 배포 | ✅ | ✅ |
| 슬립 모드 | 15분 후 | ❌ 없음 |
| 속도 | 보통 | 빠름 |
| 데이터베이스 | SQLite | PostgreSQL |
| 메모리 | 512MB | 1GB+ |

**소규모 사용에는 무료로 충분!**

---

## 🐛 문제 해결

### "배포가 실패했어요"

**Render 로그 확인:**
1. Render 대시보드 → Logs 탭
2. 빨간색 에러 메시지 확인

**흔한 문제:**
- `Module not found` → requirements.txt 확인
- `Port binding failed` → Start Command에 `--port $PORT` 있는지 확인

### "슬립 모드가 싫어요"

**해결 방법:**
1. **UptimeRobot** (무료):
   - https://uptimerobot.com 가입
   - 5분마다 자동으로 사이트 핑
   - 슬립 모드 방지

2. **유료 플랜** ($7/월):
   - 슬립 모드 완전 제거
   - 더 빠른 성능

---

## 📱 사용자에게 공유하기

배포 완료 후:

```
🏫 강의실 대여 시스템

👤 사용자: https://classroom-rental-xxxx.onrender.com/
🔐 관리자: https://classroom-rental-xxxx.onrender.com/admin

⚠️ 첫 접속 시 30초 정도 걸릴 수 있습니다 (슬립 모드)
```

---

## 🎉 완료!

이제 전세계 어디서나 접속 가능한 강의실 대여 시스템이 완성되었습니다!

**더 자세한 내용:**
- 배포 가이드: [GITHUB_DEPLOY.md](GITHUB_DEPLOY.md)
- 전체 문서: [README.md](README.md)

