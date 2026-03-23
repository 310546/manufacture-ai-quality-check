# 基础镜像（保持你原来的，比如python:3.10-slim）
FROM python:3.10-slim

# 1. 更换国内源（解决网络慢问题）+ 更新源 + 安装完整依赖
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \  # 补全完整包名
        libglib2.0-0 \     # 补充AI/图像处理常用依赖（避免后续坑）
        libsm6 \
        libxext6 \
        libxrender-dev \
    && apt-get clean \     # 清理缓存，减小镜像体积
    && rm -rf /var/lib/apt/lists/*

# 2. 后续的项目部署命令（保持你原来的）
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD ["python", "app.py"]
