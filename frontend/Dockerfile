# ============================================================
# 前端 Dockerfile — 多阶段构建（国内镜像加速版）
# ============================================================

# ---- 阶段 1: 构建 ----
FROM node:24-alpine AS builder

WORKDIR /build

# npm 走国内镜像
COPY package.json package-lock.json ./
RUN npm config set registry https://registry.npmmirror.com \
    && npm ci

COPY . .
RUN npm run build

# ---- 阶段 2: 运行 ----
FROM nginx:alpine

COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
