# Fullstack App

Vue 3 + FastAPI + SQLite 全栈应用，支持 Docker 一键部署。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Vite + Vue Router + Axios |
| 后端 | Python FastAPI + SQLAlchemy + SQLite |
| 部署 | Docker Compose / Nginx / Caddy / Cloudflare Tunnel |

## 项目结构

```
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   ├── api/            # API 请求封装
│   │   └── components/     # 通用组件
│   ├── dist/               # 构建产物
│   └── Dockerfile          # 前端 Docker 镜像
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── models.py       # 数据库模型
│   │   ├── schemas.py      # Pydantic 模型
│   │   ├── database.py     # 数据库连接
│   │   └── routes/         # API 路由
│   └── Dockerfile          # 后端 Docker 镜像
├── deploy/                 # 部署脚本与配置
├── docker-compose.yml      # Docker Compose（Nginx 反代）
├── docker-compose.simple.yml  # 最简部署（Caddy + 自动 HTTPS）
└── Caddyfile               # Caddy 配置
```

## 本地开发

### 1. 启动后端

```bash
cd backend

# 创建虚拟环境（首次）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端（http://localhost:8000）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档自动生成：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 启动前端

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器（http://localhost:5173）
npm run dev
```

### 3. 构建前端

```bash
cd frontend
npm run build
```

产物在 `frontend/dist/`。

## 生产部署（推荐）

前端部署到 GitHub Pages，后端部署到服务器。

### 架构

```
GitHub Pages                   你的服务器 (139.196.32.236)
┌──────────────┐   API 请求    ┌──────────────────────┐
│  Vue 前端    │ ───────────→  │  FastAPI 后端 :8000  │
│  (静态页面)   │               │  (Docker)            │
└──────────────┘               └──────────────────────┘
```

### 1. 部署后端到服务器

在服务器上：

```bash
# 克隆项目
git clone <你的仓库地址> /opt/fullstack-app
cd /opt/fullstack-app

# 启动后端（仅后端，端口 8000）
docker compose -f docker-compose.simple.yml up -d --build backend
```

后端启动后可通过 `http://139.196.32.236:8000` 访问。（确保服务器防火墙开放 8000 端口）

### 2. 部署前端到 GitHub Pages

前端通过 GitHub Actions 自动部署，推送代码到 `main` 分支即触发。

**首次需要手动开启 GitHub Pages：**

1. 进入仓库 → **Settings** → **Pages**
2. **Source** 选 `Deploy from a branch`
3. **Branch** 选 `gh-pages`，目录选 `/ (root)`
4. 点 **Save**

等待 Action 跑完，前端就会部署到 `https://<你的用户名>.github.io/<仓库名>/`。

### 3. 验证

1. 打开 GitHub Pages 地址，首页应显示 "🚀 全栈项目启动成功"（从后端获取数据）
2. 切换到 "📦 物品" 页，应从后端加载物品列表

## 本地开发

### 1. 启动后端

```bash
cd backend

# 创建虚拟环境（首次）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端（http://localhost:8000）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档自动生成：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 启动前端

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器（http://localhost:5173）
npm run dev
```

> 本地开发时 Vite 自带代理，API 请求转发到 `localhost:8000`，无需改 baseURL。

### 3. 构建前端

```bash
cd frontend
npm run build
```

产物在 `frontend/dist/`。

## Docker 全栈部署（一体化）

如果不需要前后端分离，也可以用 Docker 一起部署：

### 最简部署

```bash
docker compose -f docker-compose.simple.yml up -d --build
```

访问 `http://localhost` 即可。

### Nginx 反代部署

```bash
docker compose up -d --build
```

### 带 HTTPS 的部署

```bash
# Caddy 自动申请 Let's Encrypt 证书
docker compose -f docker-compose.https.yml up -d --build

# Nginx + 手动证书
docker compose -f docker-compose.nginx-https.yml up -d --build
```

### Cloudflare Tunnel 部署

```bash
docker compose -f docker-compose.tunnel.yml up -d --build
```

### 服务器一键部署

```bash
chmod +x deploy/setup-server.sh
./deploy/setup-server.sh
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 欢迎信息 |
| GET | `/api/hello` | Hello 测试 |
| GET | `/api/items` | 获取所有项目 |
| GET | `/api/items/{id}` | 获取单个项目 |
| POST | `/api/items` | 创建项目 |

### 创建项目示例

```bash
curl -X POST http://localhost:8000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "示例", "price": 9.99, "description": "描述"}'
```

## 环境变量

后端通过 `backend/.env` 配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./app.db` |
| `SECRET_KEY` | 密钥 | - |

## 常用命令

```bash
# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 重新构建并启动
docker compose up -d --build
```
