from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
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


class Project(Base):
    """作品集里的一个项目"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    # 技术栈用逗号分隔的字符串，不建关联表：
    # 前端的标签能筛选，项目的技术栈只是展示用，没有按它查询的需求
    tech = Column(String, default="")
    demo_url = Column(String, default="")   # 在线演示
    repo_url = Column(String, default="")   # 源码
    cover = Column(String, default="")      # 封面图：本站相对路径或外链
    sort = Column(Integer, default=0)       # 越大越靠前，用来手动排优先级
    published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now_cst)


class Todo(Base):
    """管理员的待办清单。整站只有一个管理员，所以没有「属于谁」这个字段"""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    done = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=now_cst)


class Image(Base):
    """文章配图，内容直接存在库里 —— 备份 = 复制 app.db 一个文件"""

    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    # 文件名（uuid.ext），同时也是 URL 里那一段，所以唯一。
    # 用文件名而不是 id 当 URL 主键，是为了历史文件（sample1.jpg）导入后地址保持不变。
    name = Column(String, nullable=False, unique=True, index=True)
    mime = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=now_cst)
