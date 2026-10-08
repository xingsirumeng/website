from datetime import datetime

from pydantic import BaseModel, field_validator


class PostCreate(BaseModel):
    title: str
    summary: str = ""
    content: str = ""
    tags: list[str] = []
    published: bool = False


class PostUpdate(BaseModel):
    """更新文章的入参。

    title 和 content 故意不给默认值：PUT 是全量替换，客户端漏传正文时应该被 422 拦下，
    而不是走默认值 "" 把文章正文静默清空 —— 那是一个不可逆的数据丢失。
    """

    title: str
    content: str
    summary: str = ""
    tags: list[str] = []
    published: bool = False


class PostResponse(BaseModel):
    """列表用，不含正文"""

    id: int
    title: str
    summary: str
    tags: list[str]
    published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("tags", mode="before")
    @classmethod
    def _tag_names(cls, values):
        """ORM 给的是 Tag 对象，对外统一成字符串数组"""
        return [t.name if hasattr(t, "name") else t for t in values]


class PostDetailResponse(PostResponse):
    content: str


class TagResponse(BaseModel):
    name: str
    count: int


class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    token: str
