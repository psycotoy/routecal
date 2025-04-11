# 1. Python 베이스 이미지 선택 (작고 빠른 slim 버전 추천)
FROM python:3.10-slim

# 2. 파이썬 환경설정 (불필요한 캐시 제거 등)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 설치를 위한 requirements 복사
COPY requirements.txt .

# 5. 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 6. 앱 전체 복사
COPY . .

# 7. gunicorn으로 앱 실행
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
