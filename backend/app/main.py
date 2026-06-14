from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import items


# 启动时自动建表（表不存在才创建，已有数据不会丢）
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Fullstack App API", version="2.0.0", lifespan=lifespan)

# 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI backend!"}
