import os

from dotenv import load_dotenv

# 本地开发时读取 backend/.env；容器里环境变量已由 compose 注入，不会被覆盖。
# 集中在这里调用，保证 database.py / auth.py 拿到的都是同一份配置，不依赖导入顺序。
load_dotenv()

# 本地开发默认 sqlite:///./app.db；容器里由 docker-compose 注入绝对路径
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# 后台 /admin 的登录密码。
# 故意不给默认值：没配置时后台拒绝一切登录（503），而不是用一个弱默认密码敞着。
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# 令牌签名密钥。未配置时退化为用 ADMIN_PASSWORD 签名 ——
# 绝不能留一个公开的默认密钥，否则知道源码的人可以自己伪造登录令牌。
SECRET_KEY = os.getenv("SECRET_KEY", "") or ADMIN_PASSWORD

# 登录令牌有效期（小时）
TOKEN_EXPIRE_HOURS = 12

# 历史图片目录。图片现在存在数据库里了，这个目录只在启动时被扫一遍，
# 用来把早期存成文件的老图片导入库（见 routes/images.py 的 import_legacy_images）。
# 导入确认无误后，这个配置和 docker-compose 里对应的挂载都可以删掉。
IMAGES_DIR = os.getenv("IMAGES_DIR", "./images")
