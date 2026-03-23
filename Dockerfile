# 基础镜像（稳定版）
FROM python:3.12-slim-bookworm

# 只安装最基础的系统工具，避免冗余
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖（不再升级pip，避免卸载问题）
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . /app

# Railway启动命令
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}"]
