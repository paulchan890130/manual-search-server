from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import openai
from flask_cors import CORS

# 🔐 환경변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🧠 Flask 인스턴스
app = Flask(__name__)
CORS(app)

# ✅ 루트 상태 확인
@app.route("/", methods=["GET"])
def index():
    return "✅ 서버 실행 중입니다.", 200

# 🔍 질문 요청
@app.route("/search", methods=["POST"])
def search():
    question = request.json.get("question", "")

    try:
        res = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 체류/사증 전문 GPT 비서입니다."},
                {"role": "user", "content": question},
            ],
            temperature=0.2,
        )
        answer = res.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"오류 발생: {str(e)}"}), 500

# 🔥 gunicorn 실행을 위한 app 노출
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
