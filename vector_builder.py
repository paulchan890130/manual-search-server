from pathlib import Path
from PyPDF2 import PdfReader
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def build_vector_store(pdf_path, vector_store_path):
    print(f"[벡터 생성] PDF: {pdf_path} → {vector_store_path}")
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    embedding_function = OpenAIEmbeddingFunction(api_key=openai_api_key)
    client = chromadb.PersistentClient(path=vector_store_path)
    collection = client.get_or_create_collection(name="manual", embedding_function=embedding_function)

    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    metadatas = [{"source": str(pdf_path)}] * len(chunks)
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    print("✅ 벡터 저장 완료")

if __name__ == "__main__":
    base_dir = Path("C:/Users/윤찬/내 드라이브/한우리 현행업무/프로그램/출입국업무관리/메뉴얼")
    stay_manuals = list(base_dir.glob("*체류민원*.pdf"))
    visa_manuals = list(base_dir.glob("*사증민원*.pdf"))

    for pdf in stay_manuals:
        build_vector_store(str(pdf), "vector_db/stay_manual")

    for pdf in visa_manuals:
        build_vector_store(str(pdf), "vector_db/visa_manual")
