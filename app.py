# app.py
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from io import BytesIO
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# ===================== 基础配置 =====================
# 配置日志（生产环境可调整为文件日志）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 加载环境变量（本地用.env，Render用平台环境变量）
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)

# ===================== 环境适配配置 =====================
# Render自动分配端口，优先读取环境变量
PORT = int(os.getenv('PORT', 5000))
# 调试模式：生产环境（Render）必须关闭
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
# CORS配置：生产环境指定具体前端域名，本地允许所有
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

# ===================== 上传安全配置 =====================
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 限制文件大小10MB
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.webp']  # 图片类型白名单
# 绝对路径：适配Render的临时文件系统，避免相对路径问题
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
# 确保上传目录存在（容错）
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ===================== CORS配置 =====================
CORS(
    app,
    resources={r"/api/*": {"origins": CORS_ORIGINS}},
    supports_credentials=True,
    methods=['POST', 'GET', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization']
)


# ===================== AI质检核心函数（无缝替换入口） =====================
def ai_quality_check(image_path):
    """
    AI质检核心逻辑 - 后续替换真实AI模型仅需修改此函数
    :param image_path: 图片本地绝对路径
    :return: dict - 质检结果（result/confidence/suggestion）
    """
    # ========== 替换示例 ==========
    # 1. 本地AI模型：加载PyTorch/TensorFlow模型推理
    # 2. 第三方API：调用阿里云/腾讯云图像识别接口
    # 3. 目前保留模拟逻辑，和原代码兼容

    logger.info(f"执行AI质检，图片路径：{image_path}")
    return {
        "result": "正常产品",
        "confidence": 98.65,
        "suggestion": "合格，可流入下一道工序"
    }


# ===================== 核心接口 =====================
@app.route('/api/quality-check', methods=['POST'])
def quality_check():
    image_path = None  # 初始化图片路径，用于finally清理
    try:
        # 1. 接收图片：优先表单文件，其次URL
        if 'image' in request.files:
            # 处理表单上传的文件
            uploaded_file = request.files['image']
            if uploaded_file.filename == '':
                raise ValueError("上传的文件名为空，请选择有效图片")

            # 安全文件名 + 时间戳（避免重复）
            filename = secure_filename(uploaded_file.filename)
            temp_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            # 校验文件类型
            file_ext = os.path.splitext(temp_filename)[1].lower()
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                raise ValueError(f"不支持的文件类型，仅支持：{','.join(app.config['UPLOAD_EXTENSIONS'])}")

            # 构建绝对路径并保存
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            uploaded_file.save(image_path)
            logger.info(f"表单上传图片已保存：{image_path}")

        else:
            # 处理URL形式的图片
            data = request.get_json() or request.form.to_dict()
            image_url = data.get('image')
            if not image_url:
                raise ValueError("未检测到图片文件或图片URL，请检查请求参数")

            # 下载图片（添加UA和超时，适配各类CDN）
            logger.info(f"开始下载远程图片：{image_url}")
            resp = requests.get(
                image_url,
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            resp.raise_for_status()  # 抛出HTTP错误（4xx/5xx）

            # 校验响应是否为图片
            if not resp.headers.get('Content-Type', '').startswith('image/'):
                raise ValueError("URL返回的内容不是有效图片，请检查URL")

            # 保存远程图片到本地
            temp_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_url.jpg"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            with open(image_path, 'wb') as f:
                f.write(resp.content)
            logger.info(f"远程图片已下载保存：{image_path}")

        # 2. 执行AI质检（核心逻辑，替换时仅改ai_quality_check函数）
        quality_result = ai_quality_check(image_path)

        # 3. 返回成功响应
        return jsonify({
            "code": 200,
            "msg": "质检成功",
            "data": quality_result
        })

    # 细分异常处理，返回精准错误信息
    except RequestEntityTooLarge:
        logger.error("上传文件超过10MB限制")
        return jsonify({"code": 413, "msg": "文件过大，最大支持10MB的图片文件"})
    except requests.exceptions.RequestException as e:
        logger.error(f"图片URL请求失败：{str(e)}")
        return jsonify({"code": 400, "msg": f"图片URL请求失败：{str(e)}"})
    except ValueError as e:
        logger.error(f"业务参数错误：{str(e)}")
        return jsonify({"code": 400, "msg": str(e)})
    except Exception as e:
        logger.error(f"服务器内部异常：{str(e)}", exc_info=True)
        return jsonify({"code": 500, "msg": "服务器内部错误，请联系管理员"})
    finally:
        # 可选：清理临时文件（Render临时文件会自动清理，也可手动清理）
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                logger.info(f"临时文件已清理：{image_path}")
            except Exception as e:
                logger.warning(f"清理临时文件失败：{str(e)}")


# ===================== 健康检查接口 =====================
@app.route('/')
def index():
    return jsonify({
        "code": 200,
        "msg": "制造业AI质检服务（Render适配版）运行正常",
        "docs": {
            "接口地址": "/api/quality-check",
            "请求方法": "POST",
            "请求方式1": "表单上传：key=image，值为图片文件",
            "请求方式2": "JSON/表单参数：key=image，值为图片URL"
        }
    })


# ===================== 启动入口 =====================
if __name__ == '__main__':
    logger.info(f"启动服务 - 端口：{PORT} | 调试模式：{DEBUG}")
    app.run(
        host='0.0.0.0',  # 允许外部访问
        port=PORT,
        debug=DEBUG,
        threaded=True  # 开启多线程，提升并发能力
    )