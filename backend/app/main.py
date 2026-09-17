import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import require_admin
from app.config import IMAGES_DIR
from app.database import engine, Base
from app.routes import posts


# 启动时自动建表（表不存在才创建，已有数据不会丢）
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
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

# 博客配图。Caddy 会把非 /api 的路径也转发过来，所以图片地址是
# https://139.196.32.236.nip.io/images/文件名
#
# 目录必须先建出来：StaticFiles 在目录不存在时不是干脆地返回 404，
# 而是抛 RuntimeError 变成 500（首次请求时检查一次）。顺带让本地开发不用手动 mkdir。
os.makedirs(IMAGES_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


@app.get("/")
def root():
    return {"message": "个人博客 API"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI backend!"}
