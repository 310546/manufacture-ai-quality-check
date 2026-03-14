from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# 初始化Flask服务
app = Flask(__name__)
CORS(app)  # 允许跨域（扣子调用必备）

# 创建图片存储文件夹
os.makedirs("static/uploads", exist_ok=True)


# ======================
# 扣子AI专用质检接口
# ======================
@app.route("/api/quality-check", methods=["POST"])
def quality_check():
    try:
        # 获取上传的图片
        file = request.files.get("image")
        if not file:
            return jsonify({"code": 400, "msg": "请上传产品图片"})

        # ==========================================
        # 模拟AI质检结果（对接扣子100%可用）
        # ==========================================
        return jsonify({
            "code": 200,
            "data": {
                "result": "正常产品",
                "confidence": 98.65,
                "suggestion": "合格，可流入下一道工序"
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": "检测失败"})


# 测试接口：服务是否运行
@app.route("/")
def home():
    return "制造业AI质检服务运行成功！"


# 启动服务
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
