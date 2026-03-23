# 用最兼容的Python3.10（避开3.12的小众兼容问题）
FROM python:3.10-slim

# 只装最核心工具，不换源（避免源配置错误）
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件（先复制requirements.txt，利用Docker缓存）
COPY requirements.txt .

# 安装依赖：只用默认pip源，不升级、不换源（避免超时/源冲突）
RUN pip install -r requirements.txt

# 复制项目代码
COPY . .

# 启动命令（简化写法，适配Railway）
CMD gunicorn app:app --bind 0.0.0.0:$PORT
