# 基础镜像：Python3.12稳定版（Railway完美兼容）
FROM python:3.12-slim

# 安装OpenCV系统依赖（解决部署报错）+ 更换国内源（解决网络慢问题）+ 更新源 + 安装完整依赖
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \  # 补全完整包名 \
        libglib2.0-0 \     # 补充AI/图像处理常用依赖 \
        libsm6 \
        libxext6 \
        libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . /app

# Railway启动命令（固定写法，适配Flask）
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}"]
