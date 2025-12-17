# 🏫 강의실 대여 시스템

FastAPI + SQLite 기반 강의실 대여/일정 관리 시스템

## ✨ 주요 기능

### 👥 사용자 (Public)
- 강의실 목록 조회
- 날짜별 사용 중 시간 확인 (상세 정보는 비공개)
- 강의실 대여 신청 (승인 대기)

### 🔐 관리자 (Admin)
- 강의실 CRUD (추가/수정/비활성화)
- 일정 관리 (수업/행사/대여)
  - **날짜 범위 선택으로 여러 날짜에 한번에 추가 가능**
- 대여 신청 승인/반려
- 일정 상세 조회/수정/삭제

## 🏢 강의실 목록

- 201호(80), 202호(90), 250호(42), 251호(68), 252호(46)
- 351호(27), 352호(24), 353호(40)
- 451호(54)
- 550호(세미나실)
- 618호 스마트 컨퍼런스홀

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
# Anaconda Python 사용 (권장)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 접속

- **사용자 페이지**: http://127.0.0.1:8000/
- **관리자 페이지**: http://127.0.0.1:8000/admin
- **API 문서**: http://127.0.0.1:8000/docs

### 4. 관리자 로그인

- **ID**: `admin`
- **비밀번호**: `admin1234`

## 📁 프로젝트 구조

```
classroom_rental/
├── backend/
│   ├── main.py              # FastAPI 앱 & API
│   ├── requirements.txt     # Python 의존성
│   └── classroom_rental.db  # SQLite 데이터베이스
├── frontend/
│   ├── user.html           # 사용자 페이지
│   └── admin.html          # 관리자 페이지
├── Dockerfile              # Docker 이미지
├── docker-compose.yml      # Docker Compose 설정
├── render.yaml             # Render.com 배포 설정
└── DEPLOY.md              # 상세 배포 가이드
```

## 🔧 기술 스택

**백엔드:**
- FastAPI (Python 웹 프레임워크)
- SQLAlchemy (ORM)
- SQLite (데이터베이스)
- JWT (인증)
- Passlib + Bcrypt (비밀번호 해싱)

**프론트엔드:**
- HTML5
- Tailwind CSS (스타일링)
- Vanilla JavaScript

## 📦 배포

다양한 배포 옵션을 지원합니다. 자세한 내용은 [DEPLOY.md](DEPLOY.md) 참고

### 빠른 배포 방법:

1. **로컬 네트워크** (같은 Wi-Fi 사용자)
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Docker**
   ```bash
   docker-compose up -d
   ```

3. **클라우드** (Render.com, Railway 등)
   - GitHub 저장소 연결
   - 자동 배포

## 🔐 보안 설정

**운영 환경에서는 반드시 변경하세요:**

```bash
# 환경 변수 설정
export JWT_SECRET="강력한-랜덤-시크릿-키"
export DEFAULT_ADMIN_PASSWORD="강력한-비밀번호"
export DB_URL="postgresql://user:pass@host/db"  # 프로덕션 DB
```

## 📝 API 엔드포인트

### Public (인증 불필요)
- `GET /public/classrooms` - 강의실 목록
- `GET /public/schedule?date=YYYY-MM-DD` - 날짜별 사용 현황
- `POST /public/reservations` - 대여 신청

### Admin (JWT 토큰 필요)
- `POST /admin/login` - 로그인
- `GET /admin/classrooms` - 강의실 관리
- `POST /admin/classrooms` - 강의실 추가
- `PATCH /admin/classrooms/{id}` - 강의실 수정
- `GET /admin/schedules` - 일정 목록
- `POST /admin/schedules` - 일정 추가
- `PATCH /admin/schedules/{id}` - 일정 수정
- `PATCH /admin/schedules/{id}/approve` - 승인
- `PATCH /admin/schedules/{id}/reject` - 반려
- `DELETE /admin/schedules/{id}` - 삭제

상세 API 문서: http://127.0.0.1:8000/docs

## 🎯 사용 시나리오

### 사용자 (학생/교직원)
1. 사용자 페이지 접속
2. 날짜와 강의실 선택
3. 사용 가능한 시간 확인
4. 대여 신청서 작성
5. 승인 대기

### 관리자
1. 관리자 페이지 로그인
2. **일정 추가** (수업/행사)
   - 시작 날짜: 2025-03-01
   - 종료 날짜: 2025-06-30
   - → 학기 전체에 자동으로 일정 추가!
3. 신청 승인/반려 처리
4. 강의실 관리

## 🐛 문제 해결

### 패키지가 설치되지 않는 경우
```bash
# Anaconda Python 사용
which python  # /opt/anaconda3/bin/python 확인
python -m pip install -r requirements.txt
```

### 포트가 사용 중인 경우
```bash
# 8000 포트 사용 프로세스 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### SSL 인증서 오류
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>
```

## 📄 라이선스

이 프로젝트는 교육/학습 목적으로 자유롭게 사용 가능합니다.

## 💡 개선 아이디어

- [ ] 이메일 알림 기능
- [ ] 엑셀 내보내기
- [ ] 반복 일정 설정 (매주 월/수/금)
- [ ] 강의실 사진 업로드
- [ ] 예약 취소 기능
- [ ] 관리자 권한 레벨 분리

---

**문의사항이나 버그 리포트는 이슈로 남겨주세요!** 🙏

