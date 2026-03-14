from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from io import BytesIO
import logging

# -------------------------- 基础配置（适配 Render） --------------------------
app = Flask(__name__)

# 1. 跨域配置：允许扣子（Coze）跨域调用，生产级宽松配置
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 2. 日志配置：方便在 Render 控制台排查问题
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 3. 临时存储：Render 为临时文件系统，无需持久化，使用内存+临时目录
UPLOAD_FOLDER = '/tmp/ai_quality_check'  # Render 推荐的临时目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 4. 端口配置：适配 Render 的 PORT 环境变量（Render 会自动分配端口）
PORT = int(os.environ.get('PORT', 5000))

# -------------------------- 核心业务逻辑（适配扣子） --------------------------
def download_image_from_url(image_url):
    """封装图片URL下载逻辑，增强容错"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = requests.get(
            image_url,
            headers=headers,
            timeout=15,
            verify=False  # 忽略证书问题（Render 部分环境可能触发）
        )
        resp.raise_for_status()  # 触发HTTP错误（4xx/5xx）
        return BytesIO(resp.content)
    except requests.exceptions.Timeout:
        raise Exception(f"图片URL请求超时：{image_url}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"图片URL返回错误：{e.response.status_code} - {image_url}")
    except Exception as e:
        raise Exception(f"下载图片失败：{str(e)}")

def ai_quality_check_core(image_path):
    """
    AI质检核心逻辑（占位）
    后续替换为真实AI：如调用Coze视觉API/本地模型/第三方图像识别接口
    """
    # 模拟质检结果（保持和扣子对接的返回格式）
    return {
        "result": "正常产品",
        "confidence": 98.65,
        "suggestion": "合格，可流入下一道工序"
    }

# -------------------------- 接口层（扣子专属适配） --------------------------
@app.route('/api/quality-check', methods=['POST'])
def quality_check():
    """
    质检接口：同时兼容
    1. 本地测试：表单上传文件（key=image）
    2. 扣子调用：JSON/Form传图片URL（key=image）
    """
    try:
        file = None
        image_source = None  # 记录图片来源，方便排查

        # 1. 优先处理表单文件（本地测试）
        if 'image' in request.files:
            file = request.files['image']
            image_source = "form_file"
            if file.filename == '':
                raise Exception("表单文件名为空")

        # 2. 兼容扣子：处理URL形式（JSON/Form传参）
        else:
            # 优先读JSON（扣子常用JSON传参），其次读Form
            data = request.get_json(silent=True) or {}  # silent=True避免JSON解析失败报错
            image_url = data.get('image') or request.form.get('image')
            
            if not image_url:
                raise Exception("未收到图片URL（扣子传参请用key=image）")
            
            logger.info(f"扣子请求：下载图片URL -> {image_url}")
            file = download_image_from_url(image_url)
            file.filename = "coze_temp.jpg"
            image_source = "coze_url"

        # 3. 保存临时文件（供后续AI调用，Render临时目录不持久化）
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_quality.jpg')
        if isinstance(file, BytesIO):
            with open(img_path, 'wb') as f:
                f.write(file.getvalue())
        else:
            file.save(img_path)
        logger.info(f"图片保存成功：{img_path}（来源：{image_source}）")

        # 4. 执行AI质检（核心逻辑，后续替换为真实模型）
        ai_result = ai_quality_check_core(img_path)

        # 5. 返回标准化结果（扣子可直接解析）
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": ai_result
        })

    # 针对性异常捕获（方便扣子端排查问题）
    except Exception as e:
        error_msg = f"质检失败：{str(e)}"
        logger.error(error_msg)
        return jsonify({
            "code": 400,
            "msg": error_msg,
            "data": None
        })

# -------------------------- 健康检查（Render 必需） --------------------------
@app.route('/')
def health_check():
    """Render 健康检查接口，部署时会检测该接口是否存活"""
    return jsonify({
        "code": 200,
        "msg": "制造业AI质检服务（Render+扣子）运行正常",
        "data": {
            "server": "render",
            "support_coze": True
        }
    })

# -------------------------- 启动服务（适配 Render） --------------------------
if __name__ == '__main__':
    # Render 生产环境必须关闭 debug，且 host 为 0.0.0.0
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False  # 生产环境绝对关闭debug！
    )