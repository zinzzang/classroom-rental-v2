#!/bin/bash

# 강의실 대여 시스템 시작 스크립트

echo "🏫 강의실 대여 시스템을 시작합니다..."
echo ""

# 현재 디렉토리 확인
cd "$(dirname "$0")/backend"

# Python 경로 확인
if command -v python &> /dev/null && python -c "import fastapi" &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null && python3 -c "import fastapi" &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ FastAPI가 설치되어 있지 않습니다."
    echo "다음 명령으로 설치하세요:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "✓ Python: $PYTHON_CMD"

# 내 IP 주소 표시
echo ""
echo "📡 네트워크 정보:"
if command -v ifconfig &> /dev/null; then
    MY_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
    if [ ! -z "$MY_IP" ]; then
        echo "  내부 IP: $MY_IP"
        echo ""
        echo "📱 다른 사람들에게 알려줄 주소:"
        echo "  👤 사용자: http://$MY_IP:8000/"
        echo "  🔐 관리자: http://$MY_IP:8000/admin"
    fi
fi

echo ""
echo "🚀 서버를 시작합니다..."
echo "   (종료하려면 Ctrl+C를 누르세요)"
echo ""

# 서버 실행
$PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

