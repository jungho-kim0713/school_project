#!/bin/bash

echo "🚨 [1/5] 학교 아카이브 관련 프로세스 종료 중..."
# 8000번 포트(Django) 사용 중인 프로세스 강제 종료
sudo fuser -k 8000/tcp
# Serveo 연결 종료 (ssh -R 명령어 찾아서 종료)
pkill -f "ssh -R 80:localhost:8000"

echo "🧹 [2/5] 기존 가상환경 및 DB 삭제 중..."
# 가상환경 삭제
rm -rf venv
# DB 삭제
rm -f db.sqlite3
# 마이그레이션 파일 초기화 (설계도 리셋)
rm -rf photo/migrations/0001_initial.py
rm -rf photo/migrations/__pycache__

echo "📦 [3/5] 새 가상환경 생성 및 패키지 설치..."
python3 -m venv venv
source venv/bin/activate
# 필수 패키지 재설치
pip install django django-allauth django-storages oci pillow python-dotenv google-generativeai PyJWT cryptography

echo "🏗️ [4/5] 데이터베이스 재구축..."
# 마이그레이션 생성 및 적용
python manage.py makemigrations photo
python manage.py migrate
# 정적 파일 모으기
python manage.py collectstatic --noinput

echo "✨ [5/5] 관리자 계정 생성 (필수!)"
echo "관리자(superuser) ID와 비밀번호를 입력해주세요."
python manage.py createsuperuser

echo "============================================="
echo "✅ 초기화 완료! 이제 아래 순서대로 실행하세요:"
echo "1. 새 터미널에서: ssh -R 80:localhost:8000 serveo.net"
echo "2. 주소 나오면: update_site.py 수정 & 구글 콘솔 등록"
echo "3. 이 터미널에서: python manage.py runserver 0.0.0.0:8000"
echo "============================================="