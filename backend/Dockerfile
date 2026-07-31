# ============================================================
# 后端 Dockerfile — FastAPI + uvicorn（国内镜像加速版）
# ============================================================
FROM python:3.13-slim

WORKDIR /app

# 换成清华 Debian 镜像源（国内加速）
RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# pip 也走清华源
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .

# 确保数据库文件目录存在且有写入权限
RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
