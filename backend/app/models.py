from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base

# 统一按东八区记录文章时间。
# 这里直接算偏移，不依赖容器的 TZ 环境变量 —— python:3.13-slim 不保证装了 tzdata，
# 设了 TZ 也可能静默不生效，那样文章日期会悄悄变成 UTC。
CST = timezone(timedelta(hours=8))


def now_cst() -> datetime:
    """当前北京时间（去掉 tzinfo，SQLite 不存时区信息）"""
    return datetime.now(CST).replace(tzinfo=None)


# 文章 ↔ 标签 的多对多关联表，由 create_all 自动创建
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)

    posts = relationship("Post", secondary=post_tags, back_populates="tags")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(String, default="")
    content = Column(Text, default="")          # Markdown 原文，渲染交给前端
    published = Column(Boolean, default=False)  # False = 草稿，前台不可见
    created_at = Column(DateTime, default=now_cst)
    updated_at = Column(DateTime, default=now_cst, onupdate=now_cst)

    # lazy="selectin"：列表接口一次查完标签，避免 N+1
    tags = relationship(
        "Tag", secondary=post_tags, back_populates="posts", lazy="selectin"
    )
