FROM python:3.10-slim

WORKDIR /skg

RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    ca-certificates \
    && update-ca-certificates 2>/dev/null || true

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y sudo nano \
    && pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple --default-timeout=300 \
    && for i in 1 2 3; do pip install -r backend/requirements.txt -i https://mirrors.aliyun.com/pypi/simple --default-timeout=300 && break || sleep 10; done

ENV TZ=Asia/Bishkek

RUN mkdir -p /var/log/celery

COPY deploy/backend/celery.conf /etc/supervisor/conf.d/

WORKDIR /skg/backend/src/

RUN chmod +x celery-start.sh

EXPOSE 8555

CMD ["./celery-start.sh"]
