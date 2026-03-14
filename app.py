from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from io import BytesIO

app = Flask(__name__)
CORS(app)  # 解决跨域问题，允许Coze调用
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# 质检接口（POST方法接收图片）
@app.route('/api/quality-check', methods=['POST'])
def quality_check():
    try:
        file = None
        # 1. 先尝试接收表单上传的文件流（适合本地测试）
        if 'image' in request.files:
            file = request.files['image']
        # 2. 兼容扣子：如果是URL形式的图片，也能接收
        else:
            # 从JSON或Form里拿图片URL
            data = request.get_json() or {}
            image_url = data.get('image') or request.form.get('image')
            if image_url:
                # 下载URL图片到内存
                resp = requests.get(image_url, timeout=10)
                resp.raise_for_status()
                file = BytesIO(resp.content)
                file.filename = "temp_from_url.jpg"

        # 校验：还是没拿到图片才返回错误
        if not file or file.filename == '':
            return jsonify({"code": 400, "msg": "请上传产品图片或有效的图片URL"})

        # 保存临时文件（后续可替换为真实AI检测）
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.jpg')
        if isinstance(file, BytesIO):
            with open(img_path, 'wb') as f:
                f.write(file.getvalue())
        else:
            file.save(img_path)

        # 模拟AI质检结果（和之前一致）
        return jsonify({
            "code": 200,
            "data": {
                "result": "正常产品",
                "confidence": 98.65,
                "suggestion": "合格，可流入下一道工序"
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务异常: {str(e)}"})


@app.route('/')
def index():
    return "制造业AI质检服务运行正常！"


if __name__ == '__main__':
    # 创建上传目录
    os.makedirs('./uploads', exist_ok=True)
    # 运行Flask服务（host='0.0.0.0'允许外部访问）
    app.run(host='0.0.0.0', port=5000, debug=True)
