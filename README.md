# Fullstack App

Vue 3 + FastAPI + SQLite 全栈应用。

- **前端** → GitHub Pages（GitHub Actions 自动部署）
- **后端** → 服务器 Docker（Caddy 自动 HTTPS）

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Vite + Vue Router + Axios |
| 后端 | Python FastAPI + SQLAlchemy + SQLite |
| 部署 | GitHub Pages + Docker + Caddy |

## 项目结构

```
├── .github/workflows/        # GitHub Actions 自动部署
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/            # 页面
│   │   ├── router/           # 路由
│   │   ├── api/              # API 请求
│   │   └── components/       # 组件
│   └── dist/                 # 构建产物
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # 入口
│   │   ├── models.py         # 数据库模型
│   │   ├── schemas.py        # Pydantic 模型
│   │   ├── database.py       # 数据库连接
│   │   └── routes/           # API 路由
│   └── Dockerfile
├── docker-compose.backend.yml  # 后端 + Caddy HTTPS
└── Caddyfile.backend           # Caddy 反代配置
```

## 本地开发

### 1. 启动后端

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API 文档: http://localhost:8000/docs

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

> 本地开发时 Vite 自带 `/api` 代理到 `localhost:8000`，不用改地址。

---

## 生产部署

### 架构

```
https://<用户名>.github.io/<仓库名>       你的服务器
┌──────────────────────┐    API     ┌──────────────────────────┐
│   Vue 前端（静态）     │ ────────→  │  Caddy :443 → 后端 :8000  │
│   托管在 GitHub Pages  │  HTTPS    │  (Docker)                │
└──────────────────────┘           └──────────────────────────┘
```

### 1. 部署后端到服务器

```bash
cd ~/website
git pull

# 启动后端 + Caddy
docker compose -f docker-compose.backend.yml up -d --build

# 确认运行
docker compose -f docker-compose.backend.yml ps
curl https://139.196.32.236.nip.io/api/hello
```

Caddy 自动申请 Let's Encrypt 证书，后端通过 HTTPS 暴露。

### 2. 部署前端

推送代码到 `main` 分支，GitHub Actions 自动构建并部署。

**首次需要：** 仓库 → Settings → Pages → Source: `Deploy from a branch` → `gh-pages` / `/(root)` → Save

---

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 欢迎 |
| GET | `/api/hello` | 测试 |
| GET | `/api/items` | 物品列表 |
| GET | `/api/items/{id}` | 单个物品 |
| POST | `/api/items` | 创建物品 |

```bash
# 创建示例
curl -X POST https://139.196.32.236.nip.io/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "示例", "price": 9.99, "description": "描述"}'
```

## 环境变量

`backend/.env`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库路径 | `sqlite:///./app.db` |
| `SECRET_KEY` | 密钥 | - |
