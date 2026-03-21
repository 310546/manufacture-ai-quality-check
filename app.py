# ==============================================
# 制造业AI智能质检系统
# 适配：本地上传文件 + 扣子JSON传图片URL
# ==============================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
import numpy as np
import requests
from dotenv import load_dotenv
# 新增：处理图片URL下载
from io import BytesIO

# 初始化配置
load_dotenv()
app = Flask(__name__)
CORS(app)

# 扣子配置
COZE_API_KEY = os.getenv("COZE_API_KEY")
COZE_BOT_ID = os.getenv("COZE_BOT_ID")
COZE_API_URL = "https://api.coze.cn/v3/chat"


# -------------------------- 新增工具函数：下载图片URL --------------------------
def download_image_from_url(image_url):
    """从URL下载图片，返回OpenCV格式的图片"""
    try:
        # 发送请求下载图片（添加超时和请求头，适配防盗链）
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(image_url, headers=headers, timeout=15)
        response.raise_for_status()  # 触发HTTP错误

        # 转换为OpenCV格式
        img_bytes = BytesIO(response.content)
        nparr = np.frombuffer(img_bytes.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        raise Exception(f"下载图片URL失败：{str(e)}")


# -------------------------- 健康检查接口 --------------------------
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "code": 200,
        "status": "运行正常",
        "project": "制造业AI智能质检系统",
        "deploy": "Railway"
    })


# -------------------------- 修改核心接口：兼容两种传参方式 --------------------------
@app.route('/api/quality-check', methods=['POST'])  # 注意：扣子调用的是这个路径！
def quality_inspect():
    try:
        img = None
        filename = "unknown.jpg"

        # 1. 优先处理扣子的JSON传参（image=URL）
        if request.is_json:
            data = request.get_json()
            image_url = data.get("image")
            if not image_url:
                return jsonify({"code": 400, "msg": "JSON参数中无image URL"}), 400
            # 下载URL图片
            img = download_image_from_url(image_url)
            filename = image_url.split("/")[-1]  # 提取URL中的文件名

        # 2. 兼容本地表单上传文件
        elif 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({"code": 400, "msg": "表单文件名为空"}), 400
            # 读取表单文件
            img_bytes = image_file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            filename = image_file.filename

        # 3. 图片校验
        if img is None:
            return jsonify({"code": 400, "msg": "图片解析失败（格式错误/URL无效）"}), 400

        # 4. 调用扣子AI（这里可以替换为你的质检逻辑，先返回模拟结果测试）
        # 【测试阶段】先返回成功，验证接口通了再对接真实AI
        return jsonify({
            "code": 200,
            "msg": "质检完成",
            "filename": filename,
            "ai_result": {
                "result": "合格",
                "confidence": 98.65,
                "suggestion": "该钟表齿轮组件为正常产品，可流入下一道工序"
            }
        })

        # 【正式使用】解开下面注释，调用扣子AI
        # headers = {
        #     "Authorization": f"Bearer {COZE_API_KEY}",
        #     "Content-Type": "application/json"
        # }
        # data = {
        #     "bot_id": COZE_BOT_ID,
        #     "user_id": "manufacture_qa",
        #     "query": f"检测{filename}图片，判断是否有划痕、污渍、变形等缺陷，返回专业质检结果",
        #     "stream": False
        # }
        # response = requests.post(COZE_API_URL, headers=headers, json=data)
        # ai_result = response.json()
        # return jsonify({
        #     "code": 200,
        #     "msg": "质检完成",
        #     "filename": filename,
        #     "ai_result": ai_result.get("content", "AI未返回结果")
        # })

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": "质检失败",
            "error": str(e)
        }), 500


# -------------------------- 启动服务 --------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)