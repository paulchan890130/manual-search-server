# app.py

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import openai
from flask_cors import CORS
from pathlib import Path
from PyPDF2 import PdfReader
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# 🔐 환경 변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🧠 Flask 앱 인스턴스 생성
app = Flask(__name__)
CORS(app)

# 📚 벡터 DB 구축 함수
def build_vector_store(pdf_path, collection_name, vector_store_path):
    print(f"[벡터 생성] PDF: {pdf_path} → {vector_store_path}/{collection_name}")
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]

    embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key)
    client = chromadb.PersistentClient(path=vector_store_path)
    collection = client.get_or_create_collection(name=collection_name, embedding_function=embedding_function)

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": str(pdf_path)}] * len(chunks)
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    print("✅ 벡터 저장 완료")

# 🧠 서버 시작시 벡터DB 구축
@app.before_serving
def init_vector_db():
    base_dir = Path("C:/Users/윤찬/내 드라이브/한우리 현행업무/프로그램/manual-search-server")
    vector_db_path = "vector_db"
    os.makedirs(vector_db_path, exist_ok=True)

    stay_files = list(base_dir.glob("*체류*.pdf"))
    visa_files = list(base_dir.glob("*사증*.pdf"))

    if stay_files and not Path(vector_db_path, "stay_manual").exists():
        build_vector_store(stay_files[0], "stay_manual", vector_db_path)

    if visa_files and not Path(vector_db_path, "visa_manual").exists():
        build_vector_store(visa_files[0], "visa_manual", vector_db_path)

# 🔍 POST 요청 처리
@app.route("/search", methods=["POST"])
def search():
    question = request.json.get("question", "")

    embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key)
    client = chromadb.PersistentClient(path="vector_db")

    # 체류민원 manual 검색
    stay_collection = client.get_collection("stay_manual", embedding_function=embedding_function)
    stay_result = stay_collection.query(query_texts=[question], n_results=3)

    # 사증민원 manual 검색
    visa_collection = client.get_collection("visa_manual", embedding_function=embedding_function)
    visa_result = visa_collection.query(query_texts=[question], n_results=3)

    context_texts = []
    for result in stay_result["documents"] + visa_result["documents"]:
        context_texts.extend(result)

    context = "\n".join(context_texts)

    prompt = f"""
    다음 메뉴얼 내용을 참고하여 질문에 답변해 주세요.

    메뉴얼 내용:
    {context}

    질문:
    {question}
    """

    try:
        res = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 체류/사증 전문 GPT 비서입니다. 메뉴얼을 기반으로 간결하게 답변하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        answer = res.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"GPT 오류: {str(e)}"}), 500

# ✅ 상태 확인용
@app.route("/", methods=["GET"])
def index():
    return "✅ 서버 실행 중입니다.", 200

# 🔥 직접 실행할 때만 서버 시작
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
else:
    application = app
