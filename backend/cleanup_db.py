#!/usr/bin/env python3
"""
데이터베이스 정리 스크립트
오래된 일정을 삭제하여 DB 크기를 관리합니다.
"""

import os
import sys
from datetime import date, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(__file__))
from main import Schedule, DB_URL

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def cleanup_old_schedules(days=180):
    """지정된 일수보다 오래된 일정 삭제"""
    cutoff_date = date.today() - timedelta(days=days)
    
    with SessionLocal() as db:
        # 오래된 일정 조회
        old_schedules = db.execute(
            select(Schedule).where(Schedule.date < cutoff_date)
        ).scalars().all()
        
        if not old_schedules:
            print(f"✅ {cutoff_date} 이전 일정이 없습니다.")
            return
        
        print(f"📅 {cutoff_date} 이전 일정 {len(old_schedules)}개 발견")
        print(f"   삭제하시겠습니까? (y/n): ", end="")
        
        response = input().lower()
        if response != 'y':
            print("❌ 취소되었습니다.")
            return
        
        # 삭제 실행
        for schedule in old_schedules:
            db.delete(schedule)
        
        db.commit()
        print(f"✅ {len(old_schedules)}개 일정이 삭제되었습니다.")

def show_stats():
    """데이터베이스 통계 표시"""
    with SessionLocal() as db:
        total = db.execute(select(Schedule)).scalars().all()
        pending = db.execute(select(Schedule).where(Schedule.status == "PENDING")).scalars().all()
        approved = db.execute(select(Schedule).where(Schedule.status == "APPROVED")).scalars().all()
        rejected = db.execute(select(Schedule).where(Schedule.status == "REJECTED")).scalars().all()
        
        cutoff_30 = date.today() - timedelta(days=30)
        cutoff_90 = date.today() - timedelta(days=90)
        cutoff_180 = date.today() - timedelta(days=180)
        
        old_30 = db.execute(select(Schedule).where(Schedule.date < cutoff_30)).scalars().all()
        old_90 = db.execute(select(Schedule).where(Schedule.date < cutoff_90)).scalars().all()
        old_180 = db.execute(select(Schedule).where(Schedule.date < cutoff_180)).scalars().all()
        
        print("\n📊 데이터베이스 통계")
        print("=" * 50)
        print(f"총 일정 수:        {len(total):5}개")
        print(f"  - PENDING:       {len(pending):5}개")
        print(f"  - APPROVED:      {len(approved):5}개")
        print(f"  - REJECTED:      {len(rejected):5}개")
        print()
        print(f"오래된 일정:")
        print(f"  - 30일 이전:     {len(old_30):5}개")
        print(f"  - 90일 이전:     {len(old_90):5}개")
        print(f"  - 180일 이전:    {len(old_180):5}개")
        print("=" * 50)
        
        # DB 파일 크기 (SQLite인 경우)
        if DB_URL.startswith("sqlite"):
            db_file = DB_URL.replace("sqlite:///./", "")
            if os.path.exists(db_file):
                size_mb = os.path.getsize(db_file) / (1024 * 1024)
                print(f"DB 파일 크기:      {size_mb:.2f} MB")
        print()

if __name__ == "__main__":
    print("🗑️  데이터베이스 정리 도구\n")
    
    show_stats()
    
    print("\n옵션을 선택하세요:")
    print("1. 180일(6개월) 이전 일정 삭제")
    print("2. 90일(3개월) 이전 일정 삭제")
    print("3. 30일(1개월) 이전 일정 삭제")
    print("4. 취소")
    print("\n선택 (1-4): ", end="")
    
    choice = input().strip()
    
    if choice == "1":
        cleanup_old_schedules(180)
    elif choice == "2":
        cleanup_old_schedules(90)
    elif choice == "3":
        cleanup_old_schedules(30)
    else:
        print("❌ 취소되었습니다.")

