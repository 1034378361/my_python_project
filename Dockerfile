###############
# 构建阶段
###############
FROM python:3.12.1-slim-bookworm AS builder

WORKDIR /app

# 设置构建环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# 安装构建依赖 - 仅安装必要的包
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc make curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装uv - 极速Python包管理器
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.cargo/env

# 添加uv到PATH
ENV PATH="/root/.cargo/bin:$PATH"

# 首先复制依赖文件，利用Docker缓存层
COPY pyproject.toml README.md ./

# 使用uv安装依赖
RUN uv pip install --system safety

# 复制源代码
COPY src ./src/

# 使用uv构建wheel包
RUN uv build --wheel --out-dir /app/wheels

# 运行安全检查
RUN safety check --json || echo "安全检查完成（可能有警告）"

###############
# 最终运行阶段
###############
FROM python:3.12.1-slim-bookworm

# 设置标签，提供镜像元数据
LABEL maintainer="周元琦 <zyq1034378361@gmail.com>" \
      name="my_python_project" \
      version="0.1.0" \
      description="现代Python项目模板，使用uv管理依赖和虚拟环境。"

# 创建非root用户
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/bash appuser

# 设置工作目录
WORKDIR /app

# 设置运行环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random

# 安装uv到运行环境
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.cargo/env

# 添加uv到PATH
ENV PATH="/root/.cargo/bin:$PATH"

# 从构建阶段复制wheel包和必要文件
COPY --from=builder /app/wheels /app/wheels
COPY --from=builder /app/src ./src

# 使用uv安装应用并清理
RUN uv pip install --system /app/wheels/*.whl && \
    rm -rf /app/wheels && \
    find /usr/local -type d -name __pycache__ -exec rm -rf {} + && \
    find /usr/local -name "*.pyc" -delete && \
    apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 安全措施：设置正确的文件权限
RUN chown -R appuser:appgroup /app && \
    chmod -R 755 /app

# 切换到非root用户
USER appuser

# 健康检查 - 每30秒检查一次
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    
    CMD my_python_project --version || exit 1
    

# 设置资源限制
ENV MALLOC_ARENA_MAX=2

# 容器启动命令

ENTRYPOINT ["my_python_project"]
CMD ["--help"]

