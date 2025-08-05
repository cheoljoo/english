# Use the latest LTS version of Node.js as the base image
FROM node:lts-slim

# 베이스 이미지로 Node.js를 사용합니다.
#FROM node:latest

# 작업 디렉토리를 설정합니다.
WORKDIR /usr/src/app

# 글로벌로 gemini-cli를 설치합니다.
RUN npm install -g @google/gemini-cli
RUN npm install youtube-data-mcp-server

# Playwright 설치 및 브라우저 설치
RUN npm install -g @playwright/test
RUN npx playwright install --with-deps

# sudo 패키지를 설치합니다.
RUN apt-get update && apt-get install -y sudo python3 python3-pip python3-venv vim git

# python3를 위한 venv, pipx를 설치하고, yfinance, pandas 등을 미리 설치합니다.
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install pipx yfinance pandas openpyxl numpy seaborn matplotlib openai python-dotenv googletrans uv

# 현재 호스트의 사용자 ID와 그룹 ID를 환경 변수로 전달합니다.
ARG USER_ID
ARG GROUP_ID

# 호스트의 설정 파일을 마운트할 디렉토리 생성
#RUN mkdir -p /home/appuser/.gemini
#RUN chmod 777 -R /home/appuser
#COPY settings.json /home/appuser/.gemini/

# 사용자와 그룹을 생성합니다.
RUN groupadd -g ${GROUP_ID} appgroup && \
    useradd -u ${USER_ID} -g appgroup -m appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 생성한 사용자로 실행되도록 설정합니다.
USER appuser

# 컨테이너가 시작될 때 호스트의 .gemini 디렉토리를 마운트합니다.
# -v <host directory>:<container directory>
#VOLUME /home/appuser/.gemini

# 컨테이너가 시작될 때 실행할 명령을 설정합니다.
CMD ["gemini", "-y"]

