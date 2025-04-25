from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/search", methods=["POST"])
def search():
    question = request.json.get("question", "")
    messages = [
        {"role": "system", "content": "당신은 체류/사증 전문 GPT 비서입니다. 메뉴얼을 기반으로 간결하게 답변하세요."},
        {"role": "user", "content": question}
    ]
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2
        )
        answer = res.choices[0].message["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"GPT 오류: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
