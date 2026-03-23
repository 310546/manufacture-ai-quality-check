# 基础镜像：用Python3.12-slim-bookworm（稳定版，比slim多一点工具但不臃肿）
FROM python:3.12-slim-bookworm

# 关键1：安装基础编译工具（解决numpy/opencv编译失败）
# 关键2：更换为中国科技大学源（比阿里更稳定）
# 关键3：--timeout=60 延长pip超时，避免下载中断
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装（加超时+中科大pip源）
COPY requirements.txt .
RUN pip install --upgrade pip==25.0.1 \
    && pip install -r requirements.txt \
        -i https://pypi.mirrors.ustc.edu.cn/simple/ \
        --trusted-host pypi.mirrors.ustc.edu.cn \
        --timeout=60

# 复制项目代码
COPY . /app

# Railway启动命令（固定写法，PORT由平台自动分配）
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}"]
