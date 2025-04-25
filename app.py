# 메뉴얼 검색 기능 (중간 서버 연동 방식 - Flask 기반 서버)

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import openai
from flask_cors import CORS
from pathlib import Path
from PyPDF2 import PdfReader
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# 🔐 환경 변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🧠 Flask 앱 인스턴스 생성
app = Flask(__name__)
CORS(app)  # CORS 설정 추가

# ✅ 루트 경로 상태 확인용
@app.route("/", methods=["GET"])
def index():
    return "✅ 서버 실행 중입니다.", 200

# 🔍 POST 요청 처리 - GPT로 질문 전달
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

# 📂 메뉴얼 PDF 자동 인식 (파일명 기준)
def get_manual_paths():
    base_dir = Path("C:/Users/윤찬/내 드라이브/한우리 현행업무/프로그램/출입국업무관리/메뉴얼")
    stay_manuals = list(base_dir.glob("*체류민원*.pdf"))
    visa_manuals = list(base_dir.glob("*사증민원*.pdf"))
    print("체류민원 매뉴얼 파일:", stay_manuals)
    print("사증민원 매뉴얼 파일:", visa_manuals)
    return stay_manuals, visa_manuals

# 📚 벡터 DB 구축 함수 구현

def build_vector_store(pdf_path, vector_store_path):
    print(f"[벡터 생성] PDF: {pdf_path} → 저장 위치: {vector_store_path}")
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key)

    # ✅ 최신 방식으로 변경
    client = chromadb.PersistentClient(path=vector_store_path)
    collection = client.get_or_create_collection(name="manual", embedding_function=embedding_function)

    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    metadatas = [{"source": str(pdf_path)}] * len(chunks)
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    print("✅ 벡터 저장 완료")

# 🔥 애플리케이션 실행
if __name__ == "__main__":
    stay_manuals, visa_manuals = get_manual_paths()
    for pdf in stay_manuals:
        build_vector_store(str(pdf), "vector_db/stay_manual")
    for pdf in visa_manuals:
        build_vector_store(str(pdf), "vector_db/visa_manual")
    app.run(host="0.0.0.0", port=10000, debug=True)
