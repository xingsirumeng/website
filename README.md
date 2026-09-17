# 个人博客

Vue 3 + FastAPI + SQLite 的个人博客，支持 Markdown 写作、标签分类、归档和草稿箱。

- **前端** → GitHub Pages（GitHub Actions 自动部署）
- **后端** → 服务器 Docker（Caddy 自动 HTTPS）

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Vite + Vue Router + Axios + marked |
| 后端 | Python FastAPI + SQLAlchemy + SQLite + PyJWT |
| 部署 | GitHub Pages + Docker + Caddy |

## 项目结构

```
├── .github/workflows/        # GitHub Actions 自动部署前端
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/            # 页面（首页/文章/标签/归档/后台）
│   │   ├── router/           # 路由（hash 模式，适配 GitHub Pages）
│   │   ├── api/              # axios 实例 + 令牌拦截器
│   │   ├── utils/            # 日期格式化
│   │   ├── types.ts          # 与后端 schema 对应的类型
│   │   └── style.css         # 全局样式 + Markdown 正文样式
│   └── dist/                 # 构建产物
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # 入口
│   │   ├── config.py         # 环境变量集中读取
│   │   ├── auth.py           # 登录令牌签发与校验
│   │   ├── models.py         # 数据库模型（Post / Tag）
│   │   ├── schemas.py        # Pydantic 模型
│   │   ├── database.py       # 数据库连接
│   │   └── routes/posts.py   # API 路由
│   ├── .env.example          # 环境变量模板
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
```

复制 `backend/.env.example` 为 `backend/.env` 并填好，然后：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API 文档: http://localhost:8000/docs
- 首次启动会自动建表，`app.db` 生成在 `backend/` 下

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

> 本地开发时 axios 用相对路径，请求经 Vite 的 `/api` 代理转发到 `localhost:8000`；生产构建才切到服务器绝对地址。

### 3. 写文章

浏览器打开 http://localhost:5173/#/admin ，输入 `ADMIN_PASSWORD` 登录即可写作。

### 4. 配图

图片存在服务器上，由后端当静态文件提供，不占仓库。

- 服务器目录：`~/website/image/`
- 本地开发目录：`backend/images/`（首次启动自动创建）
- 访问地址：`https://139.196.32.236.nip.io/images/文件名`

Markdown 里写完整 URL：

```markdown
![](https://139.196.32.236.nip.io/images/sample1.jpg)
```

上传图片（在本地执行，不是服务器上）：

```bash
scp sample1.jpg root@139.196.32.236:~/website/image/
```

> 文件名建议只用英文、数字和连字符，避免 URL 需要百分号编码。

## 生产部署

### 架构

```
https://<用户名>.github.io/<仓库名>       你的服务器
┌──────────────────────┐    API     ┌──────────────────────────┐
│   Vue 前端（静态）     │ ────────→  │  Caddy :443 → 后端 :8000  │
│   托管在 GitHub Pages  │  HTTPS    │  (Docker + SQLite volume)│
└──────────────────────┘           └──────────────────────────┘
```

### 1. 部署后端到服务器

```bash
cd ~/website
git pull

# ⚠️ 首次部署必须手动创建 backend/.env（该文件不进 git，git pull 不会生成）
cp backend/.env.example backend/.env
vim backend/.env        # 填 ADMIN_PASSWORD，并把 SECRET_KEY 换成随机串：
                        #   openssl rand -hex 32

docker compose -f docker-compose.backend.yml up -d --build

# 确认运行
docker compose -f docker-compose.backend.yml ps
curl https://139.196.32.236.nip.io/api/posts      # 应为 []
```

Caddy 自动申请 Let's Encrypt 证书，后端通过 HTTPS 暴露。**记得在云服务器安全组放行 80 和 443。**

### 2. 部署前端

推送代码到 `main` 分支，GitHub Actions 自动构建并部署。

**首次需要：** 仓库 → Settings → Pages → Source: `Deploy from a branch` → `gh-pages` / `/(root)` → Save

## API

### 公开接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/posts` | 已发布文章列表（不含正文），`?tag=` 可按标签筛选 |
| GET | `/api/posts/{id}` | 文章详情；草稿一律返回 404 |
| GET | `/api/tags` | 标签及其已发布文章数 |
| GET | `/api/hello` | 健康检查 |

### 管理接口（需要 `Authorization: Bearer <token>`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | `{password}` → `{token}`，令牌有效期 12 小时 |
| GET | `/api/admin/posts` | 全部文章，含草稿 |
| GET | `/api/admin/posts/{id}` | 单篇（草稿也能读） |
| POST | `/api/admin/posts` | 新建 |
| PUT | `/api/admin/posts/{id}` | 更新（全量） |
| DELETE | `/api/admin/posts/{id}` | 删除 |

```bash
# 发布文章的完整流程
TOKEN=$(curl -s -X POST https://139.196.32.236.nip.io/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password":"你的密码"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -X POST https://139.196.32.236.nip.io/api/admin/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"第一篇","summary":"摘要","content":"# 你好\n\n正文","tags":["随笔"],"published":true}'
```

## 环境变量

`backend/.env`（模板见 `backend/.env.example`）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库路径。本地 `sqlite:///./app.db`；容器里由 compose 注入绝对路径 | `sqlite:///./app.db` |
| `SECRET_KEY` | 登录令牌的签名密钥。留空则退化为用 `ADMIN_PASSWORD` 签名 | 回退到 `ADMIN_PASSWORD` |
| `ADMIN_PASSWORD` | 后台 `/admin` 的登录密码 | **无默认值** |

> `ADMIN_PASSWORD` 未配置时后台会拒绝一切登录并返回 503 —— 这是故意的，避免部署时漏配导致后台用一个弱默认密码敞着。

> 容器里的文章存放在 Docker volume `backend_data` 的 `/app/data/app.db`，容器重建不会丢数据。
