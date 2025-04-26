# app.py

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import openai
from flask_cors import CORS

# 🔐 환경 변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🧠 Flask 앱 인스턴스 생성
app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def index():
    return "✅ 서버 실행 중입니다.", 200

# 🔍 POST 요청 처리
@app.route("/search", methods=["POST"])
def search():
    question = request.json.get("question", "")
    messages = [
        {"role": "system", "content": "당신은 체류/사증 전문 GPT 비서입니다. 메뉴얼을 기반으로 간결하게 답변하세요."},
        {"role": "user", "content": question}
    ]

    try:
        res = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2
        )
        answer = res.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"GPT 오류: {str(e)}"}), 500

# ✅ Gunicorn용 app 노출
if __name__ != "__main__":
    app = app

# 🔥 로컬에서 실행할 때만 app.run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
