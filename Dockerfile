# 基础镜像：用Python3.12-slim即可，不用改版本
FROM python:3.12-slim

# 仅安装最基础的系统依赖（避免冗余）
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        # 仅保留pip需要的基础工具
        gcc \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 升级pip + 安装Python依赖（用清华源）
RUN pip install --upgrade pip \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . /app

# Railway启动命令
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}"]
