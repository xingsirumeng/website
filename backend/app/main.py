from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.auth import require_admin
from app.database import engine, Base
from app.routes import images, posts, projects, todos
from app.routes.images import import_legacy_images


# 启动时自动建表（表不存在才创建，已有数据不会丢）
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # 把早期存成文件的老图片导进数据库（可重复执行，导入过的不再重复导）
    import_legacy_images()
    yield


app = FastAPI(title="个人博客 API", version="1.0.0", lifespan=lifespan)

# 允许前端跨域（前端在 GitHub Pages，后端在服务器，属于跨域）
# 鉴权走 Authorization 头而不是 cookie，所以不需要 allow_credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router, prefix="/api")
app.include_router(posts.auth_router, prefix="/api/auth")
# 管理接口整个 router 统一挂鉴权依赖，以后新增管理接口不会漏掉保护
app.include_router(
    posts.admin_router, prefix="/api/admin", dependencies=[Depends(require_admin)]
)

# 博客配图存在数据库里。路径自带 /images、不带 /api 前缀，
# 因为 Caddy 会把非 /api 的路径也转发过来，图片地址形如 https://域名/images/文件名
app.include_router(images.router)
app.include_router(
    images.admin_router, prefix="/api/admin", dependencies=[Depends(require_admin)]
)

# 待办清单，全部是管理接口
app.include_router(
    todos.router, prefix="/api/admin/todos", dependencies=[Depends(require_admin)]
)

# 作品集：前台只读，后台增删改
app.include_router(projects.router, prefix="/api")
app.include_router(
    projects.admin_router, prefix="/api/admin", dependencies=[Depends(require_admin)]
)


@app.middleware("http")
async def no_sniff_images(request: Request, call_next):
    """给图片响应加 nosniff 头。

    上传的文件虽然后端会按文件头校验格式，但浏览器默认会对响应做 MIME 嗅探。
    万一有人构造出「合法 JPEG 头 + HTML 正文」的混合文件，直接访问该 URL 时
    浏览器可能把它当 HTML 执行。加上这个头就堵死了这条路，也让静态文件的
    content-type 完全以我们给的为准。
    """
    response = await call_next(request)
    if request.url.path.startswith("/images/"):
        response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/")
def root():
    return {"message": "个人博客 API"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI backend!"}
