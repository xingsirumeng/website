from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator


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


# 待办文字：先去首尾空白，再校验长度。
# 顺序很重要 —— strip_whitespace 先跑，所以纯空格会被 min_length 拦下，
# 否则「   」能通过长度检查、存进去变成空条目。
TodoText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)
]


class TodoCreate(BaseModel):
    text: TodoText


class TodoUpdate(BaseModel):
    """PATCH：两个字段都可选，只传要改的那个"""

    text: TodoText | None = None
    done: bool | None = None


class TodoResponse(BaseModel):
    id: int
    text: str
    done: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)
    tech: str = Field(default="", max_length=200)
    demo_url: str = ""
    repo_url: str = ""
    cover: str = ""
    sort: int = 0
    published: bool = True

    @field_validator("name", "tech")
    @classmethod
    def _strip(cls, value: str) -> str:
        return value.strip()

    @field_validator("demo_url", "repo_url")
    @classmethod
    def _check_link(cls, value: str) -> str:
        """必须是完整地址。光写 github.com/xxx 会被当成站内相对路径，点了就是 404"""
        value = value.strip()
        if value and not value.startswith(("http://", "https://")):
            raise ValueError("链接要以 http:// 或 https:// 开头")
        return value

    @field_validator("cover")
    @classmethod
    def _check_cover(cls, value: str) -> str:
        """封面允许两种：外链，或者本站 /images/ 下的图（后台上传后拿到的地址）"""
        value = value.strip()
        if value and not (
            value.startswith(("http://", "https://")) or value.startswith("/images/")
        ):
            raise ValueError("封面要么是 http(s) 链接，要么是本站 /images/ 下的图片")
        return value


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    token: str
