#!/bin/bash
# GitHub에 강제 푸시하는 스크립트

cd /Users/adorable/classroom_rental

echo "📦 GitHub에 파일 업로드 중..."

# RENDER_FIX.md 추가
git add RENDER_FIX.md

# 모든 파일이 추가되었는지 확인
git add .
git add backend/
git add frontend/

# 커밋 (변경사항이 있으면)
git commit -m "Fix: Add all files for deployment" || echo "변경사항 없음"

# master를 main으로 변경
git branch -M main

# GitHub의 main 브랜치에 강제 푸시
echo ""
echo "⚠️  GitHub에 푸시하려면 인증이 필요합니다."
echo ""
echo "Username: zinzzang"
echo "Password: (Personal Access Token을 입력하세요)"
echo ""

git push -f origin main

echo ""
echo "✅ 완료!"
echo ""
echo "이제 Render.com이 자동으로 재배포를 시작합니다."

