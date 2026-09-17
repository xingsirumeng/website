from datetime import datetime

from pydantic import BaseModel, field_validator


class PostCreate(BaseModel):
    title: str
    summary: str = ""
    content: str = ""
    tags: list[str] = []
    published: bool = False


class PostUpdate(PostCreate):
    pass


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
