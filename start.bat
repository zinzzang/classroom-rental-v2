@echo off
REM 강의실 대여 시스템 시작 스크립트 (Windows)

echo 🏫 강의실 대여 시스템을 시작합니다...
echo.

cd /d "%~dp0\backend"

REM Python 확인
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FastAPI가 설치되어 있지 않습니다.
    echo 다음 명령으로 설치하세요:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Python 확인 완료
echo.

REM IP 주소 표시
echo 📡 네트워크 정보:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    echo   내부 IP:%%a
    echo.
    echo 📱 다른 사람들에게 알려줄 주소:
    echo   👤 사용자: http:%%a:8000/
    echo   🔐 관리자: http:%%a:8000/admin
    goto :found
)
:found

echo.
echo 🚀 서버를 시작합니다...
echo    (종료하려면 Ctrl+C를 누르세요)
echo.

REM 서버 실행
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

