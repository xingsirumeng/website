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

# 博客配图的存放目录。
# 本地开发默认 backend/images/；容器里由 compose 注入 /app/images（挂载宿主机的 image/ 目录）
IMAGES_DIR = os.getenv("IMAGES_DIR", "./images")
