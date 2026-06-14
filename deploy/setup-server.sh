#!/usr/bin/env bash
# ============================================================
# 服务器一键部署脚本 — 零配置，自动装 Docker、构建、启动
# ============================================================
# 用法（在服务器上）:
#   1. 把项目传到服务器（或用 git clone）
#   2. chmod +x deploy/setup-server.sh
#   3. ./deploy/setup-server.sh
#   4. 脚本最后会打印出访问地址
# ============================================================
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "  Fullstack App — 一键部署"
echo "=========================================="
echo ""

# ---- 1. 安装 Docker（如果没有） ----
if ! command -v docker &>/dev/null; then
    echo "--- 1/4 安装 Docker ---"
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    echo "Docker 安装完成，可能需要重新登录"
else
    echo "--- 1/4 Docker 已安装 ✓ ---"
fi

# ---- 2. 构建前端（如果 dist 不存在） ----
if [ ! -d "$PROJECT_DIR/frontend/dist" ]; then
    echo "--- 2/4 构建前端（需要 Node.js） ---"
    if ! command -v npm &>/dev/null; then
        echo "没有 Node.js，用 Docker 构建前端..."
        docker run --rm \
            -v "$PROJECT_DIR/frontend:/app" \
            -w /app \
            node:24-alpine \
            sh -c "npm ci && npm run build"
    else
        cd "$PROJECT_DIR/frontend"
        npm ci
        npm run build
        cd "$PROJECT_DIR"
    fi
else
    echo "--- 2/4 前端已构建 ✓ ---"
fi

# ---- 3. 启动 Docker Compose ----
echo "--- 3/4 启动服务 ---"
docker compose -f docker-compose.simple.yml up -d --build

# ---- 4. 等几秒让服务就绪 ----
sleep 3

# 获取服务器 IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "你的服务器IP")

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "  访问地址:"
echo "  http://$SERVER_IP"
echo "  http://$SERVER_IP.nip.io"
echo ""
echo "  常用命令:"
echo "  查看日志:  docker compose logs -f"
echo "  重启服务:  docker compose restart"
echo "  停止服务:  docker compose down"
echo "  重新部署:  docker compose up -d --build"
echo ""
