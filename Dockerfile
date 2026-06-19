# ========== 构建阶段 ==========
FROM python:3.10-slim AS builder

WORKDIR /build

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装编译依赖
RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc && \
    rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ========== 运行阶段 ==========
FROM python:3.10-slim AS runner

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local

# 创建非 root 用户
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --gid 1001 app

# 复制项目文件（按变更频率排序以利用缓存）
COPY requirements.txt .
COPY --chown=app:app models/ models/
COPY --chown=app:app routes/ routes/
COPY --chown=app:app utils/ utils/
COPY --chown=app:app templates/ templates/
COPY --chown=app:app static/ static/
COPY --chown=app:app config.py app.py init_db.py ./

# 创建上传目录
RUN mkdir -p uploads && chown app:app uploads

# 切换到非 root 用户
USER app

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# 启动应用
CMD ["python", "app.py"]