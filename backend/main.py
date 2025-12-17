from __future__ import annotations

import os
from datetime import datetime, timedelta, date, time
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from sqlalchemy import (
    create_engine, String, Integer, Boolean, Date, Time, DateTime, Text,
    ForeignKey, select, and_
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session

from passlib.context import CryptContext
from jose import jwt, JWTError


# =========================
# Config
# =========================
DB_URL = os.getenv("DB_URL", "sqlite:///./classroom_rental.db")

DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin1234")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-prod")
JWT_ALG = "HS256"
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "240"))

OPEN_HOUR = 9
CLOSE_HOUR = 18  # end_time max 18:00

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

# 초기 강의실 목록(요구한 현황 반영)
SEED_ROOMS = [
    ("201", "201호(80)", 80),
    ("202", "202호(90)", 90),
    ("250", "250호(42)", 42),
    ("251", "251호(68)", 68),
    ("252", "252호(46)", 46),
    ("351", "351호(27)", 27),
    ("352", "352호(24)", 24),
    ("353", "353호(40)", 40),
    ("451", "451호(54)", 54),
    ("550", "550호(세미나실)", 0),
    ("618", "618호 스마트 컨퍼런스홀", 0),
]


# =========================
# DB setup
# =========================
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

class Classroom(Base):
    __tablename__ = "classrooms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)  # "201" / "CONFERENCE"
    display_name: Mapped[str] = mapped_column(String(150))
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    schedules: Mapped[List["Schedule"]] = relationship(back_populates="classroom", cascade="all, delete-orphan")

class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_super: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Schedule(Base):
    """
    '예약' + '수업/행사'를 모두 포괄하는 일정 테이블.
    사용자(public)에는 busy time만 노출하고, 상세는 admin만 조회/수정.
    """
    __tablename__ = "schedules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    # admin 전용 상세 정보
    category: Mapped[str] = mapped_column(String(30), default="CLASS")  # CLASS/SEMINAR/EVENT/RENTAL/ETC
    title: Mapped[str] = mapped_column(String(200), default="")
    owner_name: Mapped[str] = mapped_column(String(100), default="")
    owner_org: Mapped[str] = mapped_column(String(150), default="")
    memo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 승인 플로우
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)  # PENDING/APPROVED/REJECTED
    reject_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    classroom: Mapped["Classroom"] = relationship(back_populates="schedules")


def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# Auth helpers
# =========================
def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return pwd_context.verify(pw, hashed)

def create_access_token(sub: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MIN)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    admin = db.execute(select(Admin).where(Admin.username == username)).scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")
    return admin


# =========================
# Parsing / validation
# =========================
def parse_date(s: str) -> date:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (YYYY-MM-DD)")

def parse_time(s: str) -> time:
    try:
        return datetime.strptime(s, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format (HH:MM)")

def validate_time_range(st: time, et: time):
    if et <= st:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")
    open_t = time(OPEN_HOUR, 0)
    close_t = time(CLOSE_HOUR, 0)
    if st < open_t or et > close_t:
        raise HTTPException(status_code=400, detail="Time must be within 09:00~18:00")

def overlaps(st1: time, et1: time, st2: time, et2: time) -> bool:
    return (st1 < et2) and (st2 < et1)


# =========================
# Schemas
# =========================
class AdminLoginReq(BaseModel):
    username: str
    password: str

class TokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ClassroomRes(BaseModel):
    id: int
    room_code: str
    display_name: str
    capacity: int
    is_active: bool

class ClassroomCreateReq(BaseModel):
    room_code: str
    display_name: str
    capacity: int = 0

class ClassroomUpdateReq(BaseModel):
    display_name: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None

class PublicScheduleReq(BaseModel):
    classroom_id: int
    date: str
    start_time: str
    end_time: str
    name: str
    org: str
    reason: str

class AdminScheduleCreateReq(BaseModel):
    classroom_id: int
    date: str
    start_time: str
    end_time: str
    category: str = "CLASS"
    title: str = ""
    owner_name: str = ""
    owner_org: str = ""
    memo: Optional[str] = None
    status: str = "APPROVED"  # admin 등록은 기본 APPROVED 추천

class AdminScheduleUpdateReq(BaseModel):
    classroom_id: Optional[int] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    owner_name: Optional[str] = None
    owner_org: Optional[str] = None
    memo: Optional[str] = None
    status: Optional[str] = None

class RejectReq(BaseModel):
    reject_reason: str = Field(min_length=1)

class AdminScheduleRes(BaseModel):
    id: int
    classroom_id: int
    room_code: str
    display_name: str
    date: str
    start_time: str
    end_time: str
    category: str
    title: str
    owner_name: str
    owner_org: str
    memo: Optional[str]
    status: str
    reject_reason: Optional[str]
    created_at: str


# =========================
# App
# =========================
app = FastAPI(title="Classroom Rental (Final)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 운영에서는 도메인 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 (HTML) 서빙
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def root():
    """사용자 페이지로 리다이렉트"""
    return FileResponse(os.path.join(FRONTEND_DIR, "user.html"))

@app.get("/admin")
def admin_page():
    """관리자 페이지"""
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))

@app.on_event("startup")
def on_startup():
    init_db()
    with SessionLocal() as db:
        # seed classrooms if empty
        any_room = db.execute(select(Classroom.id)).scalars().first()
        if not any_room:
            for code, name, cap in SEED_ROOMS:
                db.add(Classroom(room_code=code, display_name=name, capacity=cap, is_active=True))
            db.commit()

        # seed admin
        admin = db.execute(select(Admin).where(Admin.username == DEFAULT_ADMIN_USERNAME)).scalar_one_or_none()
        if not admin:
            db.add(Admin(
                username=DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                is_super=True
            ))
            db.commit()


# =========================
# Public APIs (사용자)
# - 절대 상세 정보 노출하지 않음
# =========================
@app.get("/public/classrooms", response_model=list[ClassroomRes])
def public_list_classrooms(db: Session = Depends(get_db)):
    rooms = db.execute(
        select(Classroom).where(Classroom.is_active == True).order_by(Classroom.room_code)
    ).scalars().all()
    return [ClassroomRes(
        id=r.id, room_code=r.room_code, display_name=r.display_name, capacity=r.capacity, is_active=r.is_active
    ) for r in rooms]

def _merge_busy(intervals: list[tuple[time, time]]) -> list[tuple[time, time]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for st, et in intervals[1:]:
        last_st, last_et = merged[-1]
        if st <= last_et:  # overlap/adjacent
            merged[-1] = (last_st, max(last_et, et))
        else:
            merged.append((st, et))
    return merged

@app.get("/public/schedule")
def public_schedule(date_str: str = Query(..., alias="date"), db: Session = Depends(get_db)):
    d = parse_date(date_str)

    rooms = db.execute(
        select(Classroom).where(Classroom.is_active == True).order_by(Classroom.room_code)
    ).scalars().all()

    # PENDING/APPROVED는 시간 점유, REJECTED는 점유 X
    schedules = db.execute(
        select(Schedule).where(
            and_(Schedule.date == d, Schedule.status.in_(["PENDING", "APPROVED"]))
        )
    ).scalars().all()

    by_room: Dict[int, list[tuple[time, time]]] = {}
    for s in schedules:
        by_room.setdefault(s.classroom_id, []).append((s.start_time, s.end_time))

    out_rooms = []
    for r in rooms:
        merged = _merge_busy(by_room.get(r.id, []))
        out_rooms.append({
            "classroom_id": r.id,
            "room_code": r.room_code,
            "display_name": r.display_name,
            "capacity": r.capacity,
            "busy": [{"start": st.strftime("%H:%M"), "end": et.strftime("%H:%M")} for st, et in merged]
        })

    return {"date": d.strftime("%Y-%m-%d"), "rooms": out_rooms}

@app.post("/public/reservations")
def public_create_reservation(req: PublicScheduleReq, db: Session = Depends(get_db)):
    d = parse_date(req.date)
    st = parse_time(req.start_time)
    et = parse_time(req.end_time)
    validate_time_range(st, et)

    room = db.execute(select(Classroom).where(Classroom.id == req.classroom_id, Classroom.is_active == True)).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # 점유 검사 (PENDING/APPROVED만)
    existing = db.execute(
        select(Schedule).where(
            and_(
                Schedule.classroom_id == req.classroom_id,
                Schedule.date == d,
                Schedule.status.in_(["PENDING", "APPROVED"]),
            )
        )
    ).scalars().all()

    for s in existing:
        if overlaps(st, et, s.start_time, s.end_time):
            raise HTTPException(status_code=400, detail="이미 해당 시간에 사용 중입니다.")

    # 사용자 신청은 PENDING으로 생성
    s = Schedule(
        classroom_id=req.classroom_id,
        date=d,
        start_time=st,
        end_time=et,
        category="RENTAL",
        title="",  # 사용자에게서 받은 상세 제목은 저장하지 않음(원하면 admin 메모로만)
        owner_name=req.name.strip(),
        owner_org=req.org.strip(),
        memo=req.reason.strip(),
        status="PENDING",
    )
    db.add(s)
    db.commit()
    return {"success": True, "id": s.id}


# =========================
# Admin APIs (관리자)
# - JWT 보호
# - 상세 조회/수정/승인/반려/삭제 가능
# =========================
@app.post("/admin/login", response_model=TokenRes)
def admin_login(req: AdminLoginReq, db: Session = Depends(get_db)):
    admin = db.execute(select(Admin).where(Admin.username == req.username)).scalar_one_or_none()
    if not admin or not verify_password(req.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return TokenRes(access_token=create_access_token(sub=admin.username))

# classrooms CRUD (삭제 대신 비활성 권장)
@app.get("/admin/classrooms", response_model=list[ClassroomRes])
def admin_list_classrooms(_: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    rooms = db.execute(select(Classroom).order_by(Classroom.room_code)).scalars().all()
    return [ClassroomRes(
        id=r.id, room_code=r.room_code, display_name=r.display_name, capacity=r.capacity, is_active=r.is_active
    ) for r in rooms]

@app.post("/admin/classrooms", response_model=ClassroomRes)
def admin_create_classroom(req: ClassroomCreateReq, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    exists = db.execute(select(Classroom).where(Classroom.room_code == req.room_code)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="room_code already exists")
    r = Classroom(room_code=req.room_code, display_name=req.display_name, capacity=req.capacity, is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return ClassroomRes(id=r.id, room_code=r.room_code, display_name=r.display_name, capacity=r.capacity, is_active=r.is_active)

@app.patch("/admin/classrooms/{classroom_id}", response_model=ClassroomRes)
def admin_update_classroom(classroom_id: int, req: ClassroomUpdateReq, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    r = db.execute(select(Classroom).where(Classroom.id == classroom_id)).scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Classroom not found")
    if req.display_name is not None:
        r.display_name = req.display_name
    if req.capacity is not None:
        r.capacity = req.capacity
    if req.is_active is not None:
        r.is_active = req.is_active
    db.commit()
    db.refresh(r)
    return ClassroomRes(id=r.id, room_code=r.room_code, display_name=r.display_name, capacity=r.capacity, is_active=r.is_active)


def _to_admin_res(db: Session, s: Schedule) -> AdminScheduleRes:
    r = db.execute(select(Classroom).where(Classroom.id == s.classroom_id)).scalar_one()
    return AdminScheduleRes(
        id=s.id,
        classroom_id=s.classroom_id,
        room_code=r.room_code,
        display_name=r.display_name,
        date=s.date.strftime("%Y-%m-%d"),
        start_time=s.start_time.strftime("%H:%M"),
        end_time=s.end_time.strftime("%H:%M"),
        category=s.category,
        title=s.title,
        owner_name=s.owner_name,
        owner_org=s.owner_org,
        memo=s.memo,
        status=s.status,
        reject_reason=s.reject_reason,
        created_at=s.created_at.isoformat(),
    )

@app.get("/admin/schedules", response_model=list[AdminScheduleRes])
def admin_list_schedules(
    date_str: Optional[str] = None,
    status: Optional[str] = None,
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    q = select(Schedule)
    if date_str:
        d = parse_date(date_str)
        q = q.where(Schedule.date == d)
    if status:
        q = q.where(Schedule.status == status)

    q = q.order_by(Schedule.date.desc(), Schedule.start_time.asc())
    rows = db.execute(q).scalars().all()
    return [_to_admin_res(db, s) for s in rows]

@app.post("/admin/schedules", response_model=AdminScheduleRes)
def admin_create_schedule(req: AdminScheduleCreateReq, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    d = parse_date(req.date)
    st = parse_time(req.start_time)
    et = parse_time(req.end_time)
    validate_time_range(st, et)

    room = db.execute(select(Classroom).where(Classroom.id == req.classroom_id)).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # APPROVED/PENDING일 때만 점유. (관리자 생성이 APPROVED이면 충돌 검사 필요)
    if req.status in ["PENDING", "APPROVED"]:
        existing = db.execute(
            select(Schedule).where(
                and_(
                    Schedule.classroom_id == req.classroom_id,
                    Schedule.date == d,
                    Schedule.status.in_(["PENDING", "APPROVED"]),
                )
            )
        ).scalars().all()
        for s in existing:
            if overlaps(st, et, s.start_time, s.end_time):
                raise HTTPException(status_code=409, detail="Time conflict exists")

    s = Schedule(
        classroom_id=req.classroom_id,
        date=d,
        start_time=st,
        end_time=et,
        category=req.category,
        title=req.title,
        owner_name=req.owner_name,
        owner_org=req.owner_org,
        memo=req.memo,
        status=req.status,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return _to_admin_res(db, s)

@app.patch("/admin/schedules/{schedule_id}", response_model=AdminScheduleRes)
def admin_update_schedule(schedule_id: int, req: AdminScheduleUpdateReq, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.execute(select(Schedule).where(Schedule.id == schedule_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")

    new_classroom_id = req.classroom_id if req.classroom_id is not None else s.classroom_id
    new_date = parse_date(req.date) if req.date is not None else s.date
    new_st = parse_time(req.start_time) if req.start_time is not None else s.start_time
    new_et = parse_time(req.end_time) if req.end_time is not None else s.end_time
    validate_time_range(new_st, new_et)

    # 점유 상태가 PENDING/APPROVED면 충돌 검사
    new_status = req.status if req.status is not None else s.status
    if new_status in ["PENDING", "APPROVED"]:
        existing = db.execute(
            select(Schedule).where(
                and_(
                    Schedule.classroom_id == new_classroom_id,
                    Schedule.date == new_date,
                    Schedule.status.in_(["PENDING", "APPROVED"]),
                    Schedule.id != s.id,
                )
            )
        ).scalars().all()
        for other in existing:
            if overlaps(new_st, new_et, other.start_time, other.end_time):
                raise HTTPException(status_code=409, detail="Time conflict exists")

    s.classroom_id = new_classroom_id
    s.date = new_date
    s.start_time = new_st
    s.end_time = new_et

    if req.category is not None:
        s.category = req.category
    if req.title is not None:
        s.title = req.title
    if req.owner_name is not None:
        s.owner_name = req.owner_name
    if req.owner_org is not None:
        s.owner_org = req.owner_org
    if req.memo is not None:
        s.memo = req.memo
    if req.status is not None:
        s.status = req.status
        if s.status != "REJECTED":
            s.reject_reason = None

    db.commit()
    db.refresh(s)
    return _to_admin_res(db, s)

@app.patch("/admin/schedules/{schedule_id}/approve", response_model=AdminScheduleRes)
def admin_approve(schedule_id: int, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.execute(select(Schedule).where(Schedule.id == schedule_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if s.status != "PENDING":
        raise HTTPException(status_code=400, detail="Only PENDING can be approved")

    # 승인 충돌 체크
    existing = db.execute(
        select(Schedule).where(
            and_(
                Schedule.classroom_id == s.classroom_id,
                Schedule.date == s.date,
                Schedule.status == "APPROVED",
                Schedule.id != s.id,
            )
        )
    ).scalars().all()
    for other in existing:
        if overlaps(s.start_time, s.end_time, other.start_time, other.end_time):
            raise HTTPException(status_code=409, detail="Conflict with another approved schedule")

    s.status = "APPROVED"
    s.reject_reason = None
    db.commit()
    db.refresh(s)
    return _to_admin_res(db, s)

@app.patch("/admin/schedules/{schedule_id}/reject", response_model=AdminScheduleRes)
def admin_reject(schedule_id: int, req: RejectReq, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.execute(select(Schedule).where(Schedule.id == schedule_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if s.status != "PENDING":
        raise HTTPException(status_code=400, detail="Only PENDING can be rejected")

    s.status = "REJECTED"
    s.reject_reason = req.reject_reason.strip()
    db.commit()
    db.refresh(s)
    return _to_admin_res(db, s)

@app.delete("/admin/schedules/{schedule_id}")
def admin_delete(schedule_id: int, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.execute(select(Schedule).where(Schedule.id == schedule_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(s)
    db.commit()
    return {"success": True}

@app.delete("/admin/schedules/cleanup/old")
def cleanup_old_schedules(_: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """6개월 이전 일정 자동 삭제"""
    cutoff_date = date.today() - timedelta(days=180)
    result = db.execute(select(Schedule).where(Schedule.date < cutoff_date))
    old_schedules = result.scalars().all()
    count = len(old_schedules)
    for s in old_schedules:
        db.delete(s)
    db.commit()
    return {"success": True, "deleted_count": count, "cutoff_date": cutoff_date.strftime("%Y-%m-%d")}

@app.get("/admin/stats")
def admin_stats(_: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """시스템 통계"""
    total_rooms = db.execute(select(Classroom)).scalars().all()
    total_schedules = db.execute(select(Schedule)).scalars().all()
    pending = db.execute(select(Schedule).where(Schedule.status == "PENDING")).scalars().all()
    approved = db.execute(select(Schedule).where(Schedule.status == "APPROVED")).scalars().all()
    rejected = db.execute(select(Schedule).where(Schedule.status == "REJECTED")).scalars().all()
    
    # 6개월 이전 일정 카운트
    cutoff = date.today() - timedelta(days=180)
    old_schedules = db.execute(select(Schedule).where(Schedule.date < cutoff)).scalars().all()
    
    return {
        "total_classrooms": len(total_rooms),
        "total_schedules": len(total_schedules),
        "pending_schedules": len(pending),
        "approved_schedules": len(approved),
        "rejected_schedules": len(rejected),
        "old_schedules_count": len(old_schedules),
        "old_schedules_cutoff": cutoff.strftime("%Y-%m-%d")
    }
