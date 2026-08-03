# 파이썬 3.8 버전 환경을 도커 레벨에서 강제로 고정
FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 소스 코드 복사
COPY . /app

# 외부 라이브러리가 없으므로 pip install 과정이 아예 필요 없음
# 곧바로 실행 명령 지정
CMD ["python", "main.py"]