# 基础镜像：Python3.12稳定版（Railway完美兼容）
FROM python:3.12-slim

# 安装系统依赖（修复语法错误+修正包名+优化命令）
# 注释单独占行，避免截断续行符\
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        # 补全完整的OpenGL依赖包
        libgl1-mesa-glx \
        # AI/图像处理核心依赖（修正包名拼写）
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
    # 清理缓存，减小镜像体积
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装（用清华源加速）
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . /app

# Railway启动命令（适配Flask，PORT由Railway自动分配）
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}"]
