import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.config import IMAGES_DIR
from app.database import SessionLocal, get_db
from app.models import Image

# 公开读取：路径自带 /images，注册时不要加 /api 前缀
router = APIRouter(tags=["images"])

# 上传接口：在 main.py 注册时统一挂上 require_admin 依赖
admin_router = APIRouter(tags=["images"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024

EXT_MIME = {
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def sniff_image_ext(data: bytes) -> str | None:
    """按文件头判断真实图片类型。

    不看客户端给的 content-type，也不看文件名后缀 —— 两者都是客户端说了算的，
    把自己改名的 .html 传上来做存储型 XSS 是最常见的一类攻击。
    """
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


@router.get("/images/{name}")
def get_image(name: str, db: Session = Depends(get_db)):
    """从数据库读取图片"""
    img = db.query(Image).filter(Image.name == name).first()
    if not img:
        raise HTTPException(status_code=404, detail="图片不存在")

    return Response(
        content=img.data,
        media_type=img.mime,
        # 文件名是 uuid、内容永不改变，可以长期强缓存，省得每次打开文章都重新下载
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


@admin_router.post("/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传文章配图"""
    # 多读 1 个字节用来判断是否超限 —— 不能信 Content-Length，那个头是客户端写的
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="图片不能超过 5MB")

    ext = sniff_image_ext(data)
    if not ext:
        raise HTTPException(status_code=400, detail="只支持 JPG / PNG / GIF / WebP 图片")

    # 文件名完全由服务端生成，客户端传来的文件名直接丢弃。
    # 这样既杜绝了 ../../ 路径穿越覆盖源码，也不可能伪造出 .html 之类的后缀。
    name = f"{uuid.uuid4().hex}{ext}"
    db.add(Image(name=name, mime=EXT_MIME[ext], size=len(data), data=data))
    db.commit()

    # 返回相对地址（不返回完整 URL）：内容里存相对地址，由前端按当前环境补全成绝对地址。
    # 这样后端不需要知道自己的公网域名，本地开发上传的图也能立刻看到。
    return {"url": f"/images/{name}"}


def import_legacy_images() -> None:
    """把 IMAGES_DIR 里已有的图片文件导进数据库（迁移用，可重复执行）。

    图片早期是存文件的，改成存库之后老文件不会自动出现在库里。
    启动时跑一次，按原文件名导进去，之后那个目录就能删了。
    """
    if not os.path.isdir(IMAGES_DIR):
        return

    with SessionLocal() as db:
        for filename in sorted(os.listdir(IMAGES_DIR)):
            path = os.path.join(IMAGES_DIR, filename)
            if not os.path.isfile(path):
                continue
            # 已在库里就跳过，保证重复启动不会重复导入
            if db.query(Image).filter(Image.name == filename).first():
                continue

            mime = EXT_MIME.get(os.path.splitext(filename)[1].lower())
            if not mime:
                continue  # 不是支持的图片格式，跳过

            with open(path, "rb") as f:
                data = f.read()
            db.add(Image(name=filename, mime=mime, size=len(data), data=data))
            print(f"[启动] 已导入历史图片 {filename}")

        db.commit()
