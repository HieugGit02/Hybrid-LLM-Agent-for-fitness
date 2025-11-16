# 🥗 HINNE - NUTRITION AI CHATBOT SYSTEM

## 📋 FILES STRUCTURE

```
doanratruong/
├── 📖 ANALYSIS.md                      # Phân tích code hiện tại
├── 📖 SETUP_GUIDE.md                   # Hướng dẫn setup chi tiết
├── 📄 README.md                        # File này
│
├── 🔧 COLAB FILES (chạy ở Google Colab)
│   ├── colab_cell_api.py               # Cell Flask API (copy-paste vào Colab)
│   ├── complete_colab_setup.py         # All-in-one setup (chạy 1 cell duy nhất)
│   └── test_(2) (1).ipynb              # Notebook gốc (RAG engine)
│
├── 💻 LOCAL FILES (chạy ở máy local)
│   ├── streamlit_chatbot.py            # Streamlit frontend (UI đẹp)
│   ├── client_api.py                   # Client Python (CLI simple)
│   └── requirements_local.txt          # Python dependencies
│
├── 📊 DATA FILES
│   ├── fitness_foods_.csv              # Dữ liệu thực phẩm
│   ├── usda_foundation_foods_340_*.csv # USDA data
│   ├── FoodData_Central_foundation_*.json
│   └── *.db                            # SQLite databases
│
└── 🔄 OTHER
    └── datacrawled.py                  # Data crawling script
```

---

## 🎯 QUICK START (5 phút)

### Step 1: Google Colab (Thực hiện một lần)

1. Mở Google Colab: https://colab.research.google.com
2. Tạo notebook mới
3. Copy toàn bộ nội dung từ `complete_colab_setup.py`
4. **Sửa dòng**: `AUTH_TOKEN = "2WuXKz8T_YOUR_TOKEN_HERE"`
   - Lấy token từ: https://dashboard.ngrok.com/auth
5. Chạy cell → chờ tới khi thấy:
   ```
   🌐 PUBLIC URL: https://xxxxx-xxxxx.ngrok.io
   ```
6. **Copy URL này**

### Step 2: Máy Local

```bash
cd /home/hieuhome/CaoHoc/doanratruong

# Cài thư viện
pip install -r requirements_local.txt

# Sửa streamlit_chatbot.py
# Dòng 47: API_URL = "https://xxxxx-xxxxx.ngrok.io"

# Chạy
streamlit run streamlit_chatbot.py
```

### Step 3: Mở browser

- Truy cập http://localhost:8501
- Nhập Ngrok URL
- Chat! 🎉

---

## 🏗️ ARCHITECTURE

```
                    GOOGLE COLAB
    ┌─────────────────────────────────────┐
    │                                     │
    │  ┌─────────────────────────────┐   │
    │  │  RAG Engine                  │   │
    │  │  ├─ FAISS Vector Store       │   │
    │  │  ├─ E5 Embeddings            │   │
    │  │  ├─ CrossEncoder Reranker    │   │
    │  │  └─ Ollama LLM               │   │
    │  └─────────────────────────────┘   │
    │              ↓                      │
    │  ┌─────────────────────────────┐   │
    │  │  Flask API (Port 5000)      │   │
    │  │  POST /ask                   │   │
    │  │  GET  /health                │   │
    │  └─────────────────────────────┘   │
    │              ↓                      │
    │  ┌─────────────────────────────┐   │
    │  │  Ngrok Tunnel                │   │
    │  │  https://xxxxx.ngrok.io     │   │
    │  └─────────────────────────────┘   │
    │                                     │
    └─────────────────────────────────────┘
                    ↑        ↑        ↑
         ┌──────────┴────────┼────────┴──────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    
    LOCAL MACHINE
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Streamlit   │  │   Python     │  │    cURL /    │
    │  Frontend    │  │   Client     │  │   Postman    │
    │ (UI Dashboard)│  │ (CLI)        │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 💻 HOẠT ĐỘNG TỪNG PHẦN

### 1️⃣ **Google Colab** (Backend)

**File**: `complete_colab_setup.py` hoặc chạy cells từ `test_(2).ipynb`

**Các steps**:
1. Load dữ liệu nutrition từ SQLite DB
2. Tạo vector embeddings bằng E5 model
3. Build FAISS index để search nhanh
4. Setup CrossEncoder reranker
5. Load LLM (Ollama Gemma3)
6. Tạo Flask API + Ngrok tunnel
7. Chờ requests từ local

**Output**:
- Ngrok public URL (ví dụ: `https://1a2b-3c4d.ngrok.io`)

---

### 2️⃣ **Streamlit Frontend** (UI)

**File**: `streamlit_chatbot.py`

**Features**:
- ✅ Chat UI đẹp
- ✅ Lịch sử chat tự động
- ✅ Config Ngrok URL
- ✅ Health check endpoint
- ✅ Real-time response streaming

**Chạy**:
```bash
streamlit run streamlit_chatbot.py
```

**Truy cập**: http://localhost:8501

---

### 3️⃣ **Python Client** (CLI Alternative)

**File**: `client_api.py`

**Features**:
- ✅ Command-line interface
- ✅ Chat history
- ✅ Performance metrics
- ✅ Error handling

**Chạy**:
```bash
python client_api.py
```

---

## 🔄 DATA FLOW

```
User Query
    ↓
Streamlit/Client gửi HTTP POST
    ↓ 
{
  "query": "Ức gà bao nhiêu đạm?"
}
    ↓ (qua Ngrok tunnel)
Flask API @ Colab
    ↓
smart_ask(query)
    ↓
1. Add E5 prefix: "query: Ức gà bao nhiêu đạm?"
2. FAISS search: similarity search
3. Lấy top-20 documents
4. CrossEncoder reranking: lọc lại → top-6
5. Format context từ 6 docs
6. Call LLM (Ollama Gemma3)
7. LLM generate answer
    ↓
{
  "success": true,
  "query": "Ức gà bao nhiêu đạm?",
  "answer": "Ức gà chứa khoảng 31g đạm/100g..."
}
    ↓ (qua Ngrok tunnel)
Streamlit/Client nhận
    ↓
Hiển thị trong chat UI
```

---

## 🔧 CONFIGURATION

### Environment Variables

```bash
# Colab
DB_PATH = "/content/drive/MyDrive/test/fitness_data2.db"
FAISS_INDEX_PATH = "/content/faiss_nutrition_index"
USE_OLLAMA = True
OLLAMA_MODEL = "gemma3"
EMBED_MODEL = "intfloat/multilingual-e5-base"
K_DOCS = 6

# Ngrok
AUTH_TOKEN = "YOUR_NGROK_TOKEN" (từ https://dashboard.ngrok.com/auth)

# Local
API_URL = "https://xxxxx-xxxxx.ngrok.io" (từ Colab output)
```

### Tuning

**Nếu muốn nhanh hơn**:
```python
K_DOCS = 3              # Giảm từ 6 xuống 3
USE_OLLAMA = False      # Dùng model nhẹ
HF_MODEL_ID = "google/flan-t5-base"
```

**Nếu muốn chính xác hơn**:
```python
K_DOCS = 10             # Tăng từ 6 lên 10
EMBED_MODEL = "intfloat/multilingual-e5-large"
```

---

## 🧪 TESTING

### Test Health Check

```bash
curl -X GET https://YOUR_NGROK_URL/health
```

Response:
```json
{
  "status": "alive",
  "message": "✅ API sẵn sàng"
}
```

### Test Ask Endpoint

```bash
curl -X POST https://YOUR_NGROK_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Ức gà bao nhiêu đạm?"}'
```

Response:
```json
{
  "success": true,
  "query": "Ức gà bao nhiêu đạm?",
  "answer": "Ức gà chứa khoảng 31g đạm trên 100g..."
}
```

---

## 📊 PERFORMANCE

| Thành phần | Thời gian |
|-----------|----------|
| Vector search (FAISS) | 1-2s |
| Reranking (CrossEncoder) | 0.5-1s |
| LLM generation | 2-5s |
| **Tổng** | **4-8s** |

### Improve Performance

1. **Cache FAISS**: ✅ Đã làm
2. **Dùng model nhẹ**: Tuỳ chọn
3. **Giảm K_DOCS**: Từ 6 → 3
4. **Streaming response**: Chưa
5. **GPU**: Tuỳ Colab

---

## 🐛 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| ❌ "Connection refused" | Kiểm tra Colab cell chạy không |
| ❌ "Timeout" | Model quá nặng, giảm K_DOCS |
| ❌ "smart_ask not defined" | Chưa chạy cells 1-13 ở Colab |
| ❌ "Ngrok URL hết hiệu lực" | Chạy lại `colab_cell_api.py` |
| ❌ "Auth token invalid" | Lấy token mới từ ngrok.com |
| ❌ "Cannot read property 'answer'" | API response error, check logs |

---

## 📚 DEPENDENCIES

### Colab
- langchain >= 0.2.16
- langchain-community >= 0.2.16
- faiss-cpu
- sentence-transformers
- transformers
- torch
- flask, flask-cors
- pyngrok

### Local
- streamlit >= 1.28
- requests >= 2.31
- python-dateutil >= 2.8

---

## 🎓 LEARNING RESOURCES

- [LangChain Docs](https://python.langchain.com)
- [FAISS Guide](https://github.com/facebookresearch/faiss)
- [Streamlit Docs](https://docs.streamlit.io)
- [Ngrok Docs](https://ngrok.com/docs)

---

## 📝 NOTES

### Về Database
- Cần file `fitness_data2.db` ở Google Drive
- Schema phải có bảng `fitness_foods` với cột:
  - id, food_nameEN, food_nameVN, category, calories, protein, carbs, fat, fiber, description, usda_id

### Về LLM
- Ollama Gemma3: ~9GB VRAM
- HuggingFace models: Tuỳ model size
- 4-bit quantization: Tiết kiệm VRAM

### Về Ngrok
- Free tier: 1 URL, limited bandwidth
- Paid: Multiple URLs, 24/7 tunnels
- Auth token: Personal, không share

---

## 🚀 NEXT STEPS

1. ✅ Setup Complete Colab
2. ✅ Get Ngrok URL
3. ✅ Run Streamlit Frontend
4. 🔄 Chat & test
5. 📊 Collect feedback
6. 🔧 Fine-tune model
7. 🌐 Deploy production

---

## 👨‍💻 SUPPORT

Nếu có issue:
1. Check `ANALYSIS.md` → Code explanation
2. Check `SETUP_GUIDE.md` → Detailed setup
3. Check logs ở Colab + Local
4. Test API với cURL

---

## 📄 LICENSE

Educational project - Use freely

---

**Happy Learning! 🎉**

Hinne Nutrition AI Team
