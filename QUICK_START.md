# 🚀 QUICK START (5 PHÚT)

## Step 1: Google Colab (2 phút)

1. **Mở Colab**: https://colab.research.google.com → Notebook mới

2. **Lấy Ngrok Token**:
   - Truy cập: https://dashboard.ngrok.com/auth
   - Copy token (dài như: `2eFjsJKl8_K7x8fJ9x8...`)

3. **Copy code vào cell Colab**:
   - Mở file: `complete_colab_setup.py` 
   - Copy toàn bộ nội dung
   - Dán vào 1 cell ở Colab

4. **Sửa 1 dòng** (line ~313):
   ```python
   AUTH_TOKEN = "2WuXKz8T_YOUR_TOKEN_HERE"
   ```
   Thành:
   ```python
   AUTH_TOKEN = "YOUR_ACTUAL_TOKEN_HERE"  # Token lấy từ ngrok.com
   ```

5. **Chạy cell** → Chờ tới khi thấy:
   ```
   🌐 PUBLIC URL: https://1a2b-3c4d-5e6f.ngrok.io
   ```

6. **Copy URL này** (dùng ở bước 2 của local)

---

## Step 2: Máy Local (2 phút)

```bash
# Terminal: Mở thư mục project
cd /home/hieuhome/CaoHoc/doanratruong

# 1. Cài thư viện
pip install -r requirements_local.txt

# 2. Sửa file streamlit_chatbot.py
#    - Mở file
#    - Tìm dòng: API_URL = "https://YOUR_NGROK_URL"
#    - Sửa thành URL từ Colab (Step 1 bước 6)
#    VÍ DỤ:
#    API_URL = "https://1a2b-3c4d-5e6f.ngrok.io"

# 3. Chạy Streamlit
streamlit run streamlit_chatbot.py
```

Output:
```
  Local URL: http://localhost:8501
```

---

## Step 3: Mở Browser (1 phút)

- **URL**: http://localhost:8501
- Giao diện Streamlit sẽ hiển thị
- **Nhập Ngrok URL** (nếu chưa có)
- **Nhấn "Check Connection"** → Xanh ✅ = OK
- **Gõ câu hỏi**: "Ức gà bao nhiêu đạm?"
- **Nhấn Enter** → Chờ API trả lời

---

## ✅ ĐẠT YÊU CẦU?

✓ Code hoạt động ổn
✓ Streamlit frontend (UI đẹp)
✓ Flask API ở Colab
✓ Ngrok tunnel kết nối Colab ↔ Local
✓ Client Python test

---

## 🆘 NẾU LỖI

### "Connection refused"
→ Colab cell chưa chạy xong

### "Timeout"
→ Chạy lâu, chờ 30s

### "URL không đúng"
→ Copy lại URL từ Colab output

### "smart_ask not defined"
→ Chưa chạy cells 1-13 trước

---

## 📝 CÁCH CHẠY CLIENT Python (Alternative)

Nếu không muốn Streamlit:

```bash
python client_api.py
```

Nhập URL Ngrok, rồi chat ở CLI

---

**Done! 🎉 Hệ thống sẵn sàng**
