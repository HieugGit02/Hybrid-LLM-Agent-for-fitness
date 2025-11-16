"""
=====================================================
COMPLETE NOTEBOOK CELL FOR COLAB (ALL-IN-ONE)
=====================================================
Chạy file này ở một cell trong Google Colab để có đủ:
1. Data loading
2. Vector store setup  
3. LLM initialization
4. Flask API + Ngrok

sau đó API sẽ ready để call từ local!
"""

# =====================================================
# CELL 0: IMPORTS & SETUP BAN ĐẦU
# =====================================================

import os
import sqlite3
import json
import warnings
import torch
import re
from typing import List
from datetime import datetime

warnings.filterwarnings("ignore")

print("=" * 70)
print("🚀 HINNE - NUTRITION AI (COLAB SETUP)")
print("=" * 70 + "\n")

# =====================================================
# CELL 1: CÀI ĐẶT DEPENDENCIES
# =====================================================

print("📦 STEP 1: Cài đặt thư viện...\n")

packages = [
    "langchain>=0.2.16",
    "langchain-community>=0.2.16",
    "faiss-cpu",
    "sentence-transformers",
    "transformers",
    "accelerate",
    "bitsandbytes",
    "flask",
    "flask-cors",
    "pyngrok"
]

import subprocess
for pkg in packages:
    subprocess.run(["pip", "install", "-q", pkg], check=False)

print("✅ Tất cả thư viện đã cài đặt\n")

# =====================================================
# CELL 2: IMPORT LIBRARIES
# =====================================================

print("📚 STEP 2: Import libraries...\n")

from google.colab import drive
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_community.llms import Ollama
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok

print("✅ Imports thành công\n")

# =====================================================
# CELL 3: MOUNT GOOGLE DRIVE & SETUP PATHS
# =====================================================

print("💾 STEP 3: Mount Google Drive...\n")

drive.mount("/content/drive")

DB_PATH = "/content/drive/MyDrive/test/fitness_data2.db"
FAISS_INDEX_PATH = "/content/faiss_nutrition_index"

EMBED_MODEL = "intfloat/multilingual-e5-base"
EMBED_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
K_DOCS = 6

USE_OLLAMA = True
OLLAMA_MODEL = "gemma3"
HF_MODEL_ID = "google/gemma-3-12b-it-qat"

print(f"✅ DB_PATH: {DB_PATH}")
print(f"✅ EMBED_DEVICE: {EMBED_DEVICE}")
print(f"✅ USE_OLLAMA: {USE_OLLAMA}\n")

# =====================================================
# CELL 4: LOAD DATA & CREATE VECTOR STORE
# =====================================================

print("🗂️  STEP 4: Load data từ DB...\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, food_nameEN, food_nameVN, category,
           calories, protein, carbs, fat, fiber,
           description, usda_id
    FROM fitness_foods
""")
rows = cursor.fetchall()
conn.close()

if not rows:
    raise RuntimeError("❌ Database trống!")

print(f"✅ Đã load {len(rows)} thực phẩm\n")

# =====================================================
# CELL 5: PROCESS TEXT & METADATA
# =====================================================

print("🔄 STEP 5: Xử lý text & metadata...\n")

texts, metadatas = [], []

for row in rows:
    (id_, food_en, food_vn, category,
     cal, p, c, f, fi,
     desc, usda_id) = row

    text = (
        f"Tên: {food_vn} (Tên tiếng Anh: {food_en}). "
        f"Loại: {category}. "
        f"Mô tả: {desc}. "
        f"Dinh dưỡng (mỗi 100g): "
        f"{cal} calories (kcal), "
        f"{p}g protein (đạm), "
        f"{f}g fat (chất béo), "
        f"{c}g carbohydrates (carbs, tinh bột), "
        f"{fi}g fiber (chất xơ). "
        f"(USDA ID: {usda_id})"
    )
    texts.append(text)

    metadatas.append({
        "id": id_,
        "name": food_vn,
        "name_en": food_en,
        "category": category,
        "usda_id": usda_id,
        "calories": cal,
        "protein": p,
        "carbs": c,
        "fat": f,
        "fiber": fi,
        "description": desc,
        "primary_goal": f"Cung cấp dinh dưỡng {category}",
        "pro_tips_vn": f"Chia nhỏ khẩu phần {food_vn} để tối ưu hóa hấp thu",
        "comparison_notes_vn": f"{food_vn} có hàm lượng {p}g đạm/100g"
    })

print(f"✅ Đã xử lý {len(texts)} văn bản\n")

# =====================================================
# CELL 6: CREATE EMBEDDINGS & FAISS INDEX
# =====================================================

print("🧠 STEP 6: Tạo embeddings & FAISS index...\n")

embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": EMBED_DEVICE},
    encode_kwargs={"normalize_embeddings": True},
)

if os.path.exists(FAISS_INDEX_PATH):
    print(f"📥 Load FAISS index từ: {FAISS_INDEX_PATH}")
    vectorstore = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
else:
    print("🔨 Tạo FAISS index mới...")
    texts_prefixed = [f"passage: {t}" for t in texts]
    vectorstore = FAISS.from_texts(texts_prefixed, embeddings, metadatas=metadatas)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"💾 Lưu index tại: {FAISS_INDEX_PATH}")

print("✅ Vector store ready\n")

# =====================================================
# CELL 7: SETUP RETRIEVER & RERANKER
# =====================================================

print("🔍 STEP 7: Setup retriever & reranker...\n")

base_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 20}
)

hf_ce = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
reranker = CrossEncoderReranker(model=hf_ce, top_n=K_DOCS)

compression_retriever = ContextualCompressionRetriever(
    base_retriever=base_retriever,
    base_compressor=reranker
)

print("✅ Retriever & reranker ready\n")

# =====================================================
# CELL 8: SETUP LLM
# =====================================================

print("🤖 STEP 8: Setup LLM...\n")

if USE_OLLAMA:
    print("   Dùng Ollama backend (gemma3)")
    llm = Ollama(model=OLLAMA_MODEL, temperature=0)
else:
    print("   Dùng HuggingFace backend")
    def build_hf_llm(model_id=HF_MODEL_ID, temperature=0, max_new_tokens=512):
        tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        kwargs = dict(
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        if torch.cuda.is_available():
            kwargs["load_in_4bit"] = True
        mdl = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
        gen = pipeline(
            "text-generation",
            model=mdl,
            tokenizer=tok,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=temperature,
            pad_token_id=tok.eos_token_id
        )
        return HuggingFacePipeline(pipeline=gen)
    llm = build_hf_llm()

print("✅ LLM ready\n")

# =====================================================
# CELL 9: DEFINE HELPER FUNCTIONS
# =====================================================

print("🛠️  STEP 9: Define helper functions...\n")

def clean_output(text: str) -> str:
    """Làm sạch output"""
    text = re.sub(r'[🐟🐮🐓💦💪🤔😊]', '', text)
    text = text.replace('```', '').strip()
    greetings = ['Chào!', 'Chào bạn!', 'Cảm ơn', 'Chúc bạn']
    for g in greetings:
        text = text.replace(g, '')
    if "Final Answer:" in text:
        text = text.split("Final Answer:")[-1].strip()
    return text.strip()

def format_docs(docs):
    """Format documents để hiển thị"""
    lines = []
    for i, d in enumerate(docs, 1):
        m = d.metadata
        goal = m.get('primary_goal', 'Chưa rõ')
        tips = m.get('pro_tips_vn', 'Chưa có mẹo')
        comp = m.get('comparison_notes_vn', 'Chưa có so sánh')

        lines.append(
            f"- #{i} | {m.get('name')} (EN: {m.get('name_en')}) | Loại: {m.get('category')}\n"
            f"  Dinh dưỡng/100g: {m.get('calories')} kcal; {m.get('protein')}g đạm; {m.get('carbs')}g carb; {m.get('fat')}g béo.\n"
            f"  Mục tiêu: {goal}\n"
            f"  Mẹo: {tips}\n"
            f"  So sánh: {comp}"
        )
    return "\n".join(lines)

def add_e5_query_prefix(q: str) -> str:
    """Add E5 query prefix"""
    return "query: " + q

print("✅ Helper functions ready\n")

# =====================================================
# CELL 10: DEFINE smart_ask()
# =====================================================

print("🧠 STEP 10: Define smart_ask()...\n")

def smart_ask(query: str):
    """Main query function with routing"""
    query_lower = query.lower()

    NUTRITION_KEYWORDS = [
        'calo', 'đạm', 'protein', 'béo', 'fat', 'carb', 'carbohydrate',
        'chất xơ', 'fiber', 'bao nhiêu', 'mấy gam', 'thành phần',
        'gà', 'bò', 'cá', 'táo', 'chuối', 'rau', 'thịt', 'trứng'
    ]

    GREETING_KEYWORDS = ['chào', 'hi', 'hello', 'bạn là ai', 'tên gì']

    if any(word in query_lower for word in NUTRITION_KEYWORDS):
        try:
            docs = compression_retriever.get_relevant_documents(
                add_e5_query_prefix(query)
            )

            if not docs:
                return "Xin lỗi, tôi không có thông tin về thực phẩm này."

            context = format_docs(docs)

            fallback_prompt_template = f"""
Bạn là trợ lý AI Hinne, một chuyên gia dinh dưỡng thể hình.
Chỉ dựa vào thông tin dưới đây để trả lời câu hỏi.

# THÔNG TIN TRA CỨU (dinh dưỡng mỗi 100g):
{context}

# CÂU HỎI:
{query}

# QUY TẮC BẮT BUỘC:
1. LUÔN dùng Tiếng Việt.
2. Trả lời câu hỏi chính.
3. SAU ĐÓ, dùng "Mẹo" và "So sánh" để giải thích.
4. KHÔNG ĐƯỢC bịa số liệu.

# TRẢ LỜI:
"""

            answer = llm.invoke(fallback_prompt_template).strip()
            return clean_output(answer)

        except Exception as e:
            return f"Lỗi: {e}"

    elif any(word in query_lower for word in GREETING_KEYWORDS):
        return "Chào bạn! Tôi là Hinne, trợ lý dinh dưỡng AI."

    else:
        try:
            docs = compression_retriever.get_relevant_documents(
                add_e5_query_prefix(query)
            )
            if not docs:
                return "Tôi không hiểu câu hỏi. Hỏi tôi về dinh dưỡng thực phẩm?"

            context = format_docs(docs)
            fallback_prompt_template = f"Dựa vào: {context}.\n\nCâu hỏi: {query}"
            answer = llm.invoke(fallback_prompt_template).strip()
            return clean_output(answer)

        except Exception as e:
            return f"Lỗi: {e}"

print("✅ smart_ask() ready\n")

# =====================================================
# CELL 11: SETUP FLASK API + NGROK
# =====================================================

print("🚀 STEP 11: Setup Flask API + Ngrok...\n")

app = Flask(__name__)
CORS(app)

@app.route('/ask', methods=['POST'])
def ask_endpoint():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({"success": False, "error": "Query trống"}), 400

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 {query[:80]}")
        answer = smart_ask(query)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Trả lời\n")

        return jsonify({"success": True, "query": query, "answer": answer})

    except Exception as e:
        print(f"[ERROR] {e}\n")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive", "message": "✅ API sẵn sàng"})

@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        "name": "Hinne - Nutrition AI",
        "version": "1.0",
        "endpoints": ["POST /ask", "GET /health", "GET /info"]
    })

print("✅ Flask app created\n")

# =====================================================
# CELL 12: CREATE NGROK TUNNEL
# =====================================================

print("📡 STEP 12: Create Ngrok tunnel...\n")

# SET AUTH TOKEN HERE!
AUTH_TOKEN = "2WuXKz8T_YOUR_TOKEN_HERE"  # ← UPDATE THIS!

if AUTH_TOKEN == "2WuXKz8T_YOUR_TOKEN_HERE":
    print("⚠️  CHƯA CÀI NGROK AUTH TOKEN!")
    print("    1. Truy cập: https://dashboard.ngrok.com/auth")
    print("    2. Copy token")
    print("    3. Sửa dòng: AUTH_TOKEN = \"YOUR_TOKEN\"")
    print()
else:
    ngrok.set_auth_token(AUTH_TOKEN)
    print("✅ Ngrok auth token set\n")

public_url = ngrok.connect(5000)

print("=" * 70)
print("✅ NGROK TUNNEL READY!")
print("=" * 70)
print(f"\n🌐 PUBLIC URL: {public_url}\n")
print(f"📝 ENDPOINTS:\n")
print(f"   POST {public_url}/ask - Gửi câu hỏi")
print(f"   GET  {public_url}/health - Kiểm tra")
print(f"   GET  {public_url}/info - Thông tin\n")
print(f"💡 NEXT STEPS:\n")
print(f"   1. Copy URL trên\n")
print(f"   2. Mở streamlit_chatbot.py trên local\n")
print(f"   3. Sửa: API_URL = \"{public_url}\"\n")
print(f"   4. Chạy: streamlit run streamlit_chatbot.py\n")
print("=" * 70 + "\n")

# =====================================================
# CELL 13: RUN FLASK SERVER
# =====================================================

print("🔄 STEP 13: Start Flask server at 0.0.0.0:5000...\n")
print("📨 Server đang chờ request từ local client...\n")
print("⚠️  ĐỪ TẮT CELL NÀY! Nó sẽ chạy liên tục.\n")
print("=" * 70 + "\n")

# Run server (blocking)
app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
