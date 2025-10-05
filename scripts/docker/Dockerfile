# EasyProxy Docker 镜像
# 多阶段构建,优化镜像大小

# ===== 构建阶段 =====
FROM python:3.11-slim as builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖到独立目录
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 复制源代码
COPY . .

# 安装 easyproxy
RUN pip install --no-cache-dir --prefix=/install .

# ===== 运行阶段 =====
FROM python:3.11-slim

LABEL maintainer="Slothtron <lolioycmd@foxmail.com>"
LABEL description="EasyProxy Multi-Protocol Proxy Server"
LABEL version="0.1.0"

# 创建非 root 用户
RUN groupadd -r easyproxy && \
    useradd -r -g easyproxy -s /sbin/nologin -c "EasyProxy user" easyproxy

# 创建必要的目录
RUN mkdir -p /etc/easyproxy /var/log/easyproxy && \
    chown -R easyproxy:easyproxy /etc/easyproxy /var/log/easyproxy

# 从构建阶段复制安装的包
COPY --from=builder /install /usr/local

# 复制默认配置文件
COPY config/config.example.yaml /etc/easyproxy/config.yaml
RUN chown easyproxy:easyproxy /etc/easyproxy/config.yaml

# 切换到非 root 用户
USER easyproxy

# 工作目录
WORKDIR /home/easyproxy

# 暴露端口
EXPOSE 7899

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('127.0.0.1', 7899)); s.close()" || exit 1

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 入口点
ENTRYPOINT ["easyproxy"]

# 默认命令
CMD ["start", "-c", "/etc/easyproxy/config.yaml"]
