#!/usr/bin/env bash
# ============================================================
# 一键部署脚本（在服务器上运行）
#   用法: chmod +x deploy.sh && ./deploy.sh
# ============================================================
set -e

APP_DIR="/var/www/fullstack-app"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

echo "===== 1/5 创建目录 ====="
sudo mkdir -p "$APP_DIR"

echo "===== 2/5 部署后端 ====="
sudo cp -r "$(dirname "$0")/../backend" "$BACKEND_DIR"
cd "$BACKEND_DIR"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install -r requirements.txt

echo "===== 3/5 配置 systemd ====="
sudo cp "$(dirname "$0")/fullstack-app.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fullstack-app
sudo systemctl restart fullstack-app

echo "===== 4/5 配置 Nginx ====="
sudo cp "$(dirname "$0")/fullstack-app.nginx.conf" /etc/nginx/sites-available/fullstack-app
sudo ln -sf /etc/nginx/sites-available/fullstack-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "===== 5/5 完成 ====="
echo "后端状态:"
sudo systemctl status fullstack-app --no-pager -l | head -5
echo ""
echo "部署完成！访问 http://$(curl -s ifconfig.me) 查看"
