from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import create_token, verify_password
from app.config import ADMIN_PASSWORD
from app.database import get_db
from app.models import Post, Tag
from app.schemas import (
    LoginRequest,
    PostCreate,
    PostDetailResponse,
    PostResponse,
    PostUpdate,
    TagResponse,
    TokenResponse,
)

# 公开接口：文章列表 / 详情 / 标签
router = APIRouter(tags=["posts"])

# 登录接口单独放，因为登录本身不能要求已经登录
auth_router = APIRouter(tags=["auth"])

# 管理接口：在 main.py 注册时统一挂上 require_admin 依赖
admin_router = APIRouter(tags=["admin"])


def _resolve_tags(db: Session, names: list[str]) -> list[Tag]:
    """标签名数组转成 Tag 对象：去掉空白、去重、没有的建出来"""
    tags = []
    seen = set()
    for raw in names:
        name = raw.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)
    return tags


def _cleanup_orphan_tags(db: Session) -> None:
    """删掉已经没有任何文章引用的标签"""
    for tag in db.query(Tag).all():
        if not tag.posts:
            db.delete(tag)
    db.commit()


@auth_router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """用管理员密码换登录令牌"""
    if not ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="服务端未配置 ADMIN_PASSWORD")
    if not verify_password(payload.password):
        raise HTTPException(status_code=401, detail="密码错误")
    return {"token": create_token()}


# ---------- 公开接口 ----------


@router.get("/posts", response_model=list[PostResponse])
def list_posts(tag: str | None = None, db: Session = Depends(get_db)):
    """已发布文章列表（不含正文），可用 ?tag= 按标签筛选"""
    query = db.query(Post).filter(Post.published.is_(True))
    if tag:
        query = query.filter(Post.tags.any(Tag.name == tag))
    # 再按 id 倒序是为了同一时间创建的文章顺序稳定
    return query.order_by(Post.created_at.desc(), Post.id.desc()).all()


@router.get("/posts/{post_id}", response_model=PostDetailResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """文章详情，草稿对外一律当作不存在"""
    post = (
        db.query(Post)
        .filter(Post.id == post_id, Post.published.is_(True))
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


@router.get("/tags", response_model=list[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    """标签及各自的已发布文章数"""
    rows = (
        db.query(Tag.name, func.count(Post.id))
        .select_from(Tag)
        .join(Tag.posts)
        .filter(Post.published.is_(True))
        .group_by(Tag.id)
        .order_by(func.count(Post.id).desc(), Tag.name)
        .all()
    )
    return [{"name": name, "count": count} for name, count in rows]


# ---------- 管理接口（已由 main.py 统一鉴权）----------


@admin_router.get("/posts", response_model=list[PostResponse])
def admin_list_posts(db: Session = Depends(get_db)):
    """后台列表：包含草稿"""
    return db.query(Post).order_by(Post.updated_at.desc(), Post.id.desc()).all()


@admin_router.get("/posts/{post_id}", response_model=PostDetailResponse)
def admin_get_post(post_id: int, db: Session = Depends(get_db)):
    """后台读取单篇，草稿也能看，用于编辑和预览"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


@admin_router.post("/posts", response_model=PostDetailResponse)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    post = Post(
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        published=payload.published,
        tags=_resolve_tags(db, payload.tags),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@admin_router.put("/posts/{post_id}", response_model=PostDetailResponse)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    post.title = payload.title
    post.summary = payload.summary
    post.content = payload.content
    post.published = payload.published
    post.tags = _resolve_tags(db, payload.tags)

    db.commit()
    _cleanup_orphan_tags(db)
    db.refresh(post)
    return post


@admin_router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    db.delete(post)
    db.commit()
    _cleanup_orphan_tags(db)
    return {"message": "已删除"}
