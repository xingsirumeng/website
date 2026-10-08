# ============================================================
# 后端 Dockerfile — FastAPI + uvicorn（国内镜像加速版）
# ============================================================
FROM python:3.13-slim

WORKDIR /app

# 换成阿里云 Debian 镜像源
# 用阿里云而不是清华源：这台服务器就在阿里云上，走内网、不计公网流量、也不受公网波动影响。
# （曾经用清华源，出现过宿主机能访问、构建时却拿不到任何包的情况）
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# pip 同样走阿里云源
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

COPY . .

# 确保数据库文件目录存在且有写入权限
RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
