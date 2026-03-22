# 基础镜像：Python3.12稳定版（Railway完美兼容）
FROM python:3.12-slim

# 安装OpenCV系统依赖（解决部署报错）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# Railway启动命令（固定写法，适配Flask）
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}"]