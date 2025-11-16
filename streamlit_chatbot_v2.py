"""
=====================================================
STREAMLIT CHATBOT FRONTEND V2 - MODERN UI
=====================================================
Cách chạy:
  streamlit run streamlit_chatbot_v2.py

Cấu hình:
  - Sửa API_URL bên dưới để điền Ngrok URL từ Colab
  - Input sticky (dính ở dưới cùng)
  - Thiết kế modern, responsive
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time

# =====================================================
# ⚙️ CẤU HÌNH
# =====================================================

API_URL = "https://3925ecede99e.ngrok-free.app"  # ← SỬA ĐÂY

# =====================================================
# 🎨 STREAMLIT CONFIG
# =====================================================
st.set_page_config(
    page_title="Hinne - Nutrition AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "api_url" not in st.session_state:
    st.session_state["api_url"] = API_URL
if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================
# 🎨 ADVANCED CSS STYLING (Modern UI + Sticky Input)
# =====================================================
st.markdown("""
<style>
  :root{--bg:#f7f8fb;--card:#ffffff;--muted:#6b7280;--accent:#2563eb;--accent-2:#7c3aed}
  .main{padding:0 !important;background:var(--bg)}
  .block-container{padding-top:1rem;padding-bottom:140px}
  .header-container{background:transparent;padding:1.25rem 0 0.75rem 0;margin-bottom:0.5rem;text-align:left}
  .header-title{font-size:1.5rem;font-weight:700;color:#0f172a;margin:0}
  .header-subtitle{color:var(--muted);margin-top:0.25rem;font-size:0.95rem}
  .chat-container{max-height:calc(100vh - 220px);overflow-y:auto;padding:1rem 0;scroll-behavior:smooth}
  .chat-message{background:var(--card);padding:0.9rem 1rem;border-radius:10px;margin:0.6rem 1rem;box-shadow:0 1px 2px rgba(15,23,42,0.04);display:flex;gap:0.6rem}
  .user-message{align-self:flex-end;background:linear-gradient(90deg,var(--accent),var(--accent-2));color:white;margin-left:20%;max-width:75%}
  .bot-message{align-self:flex-start;background:#f3f4f6;color:#0f172a;margin-right:20%;max-width:75%}
  .error-message{align-self:center;background:#fee2e2;color:#991b1b}
  .message-icon{font-size:1.2rem;min-width:2rem;text-align:center}
  .message-content{flex:1;line-height:1.5}
  .message-time{font-size:0.75rem;color:var(--muted);margin-top:0.4rem}
  .input-container{position:fixed;left:0;right:0;bottom:0;background:linear-gradient(180deg,var(--card),#fcfcff);padding:12px 16px;border-top:1px solid #e6e7ee;box-shadow:0 -8px 24px rgba(2,6,23,0.06);z-index:999}
  .input-row{max-width:1100px;margin:0 auto;display:flex;gap:8px}
  .input-box{flex:1;border:1px solid #e6e7ee;padding:10px 12px;border-radius:10px;font-size:0.95rem}
  .send-btn{background:var(--accent);color:white;padding:10px 14px;border-radius:8px;border:none;font-weight:600}
  .send-btn:active{transform:translateY(1px)}
  [data-testid="stSidebar"]{background:transparent}
  @media (max-width:768px){.chat-message{margin:0.5rem}.user-message,.bot-message{max-width:90%}.input-row{padding:0 8px}}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 📊 SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2 style="margin: 0; font-size: 1.5rem;">⚙️ Cài Đặt</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Quản lý kết nối API</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API URL Configuration
    st.subheader("🌐 Ngrok API")
    api_input = st.text_input(
        "Nhập URL từ Colab:",
        value=st.session_state.get("api_url", API_URL),
        placeholder="https://xxxxx.ngrok-free.app",
        help="Dán URL Ngrok từ Colab ở đây"
    )
    
    if api_input and api_input != st.session_state.get("api_url"):
        new_url = api_input.rstrip('/')
        st.session_state["api_url"] = new_url
        st.success("✅ URL cập nhật thành công!")
    
    # Health Check
    st.subheader("🔌 Kiểm Tra Kết Nối")
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        if st.button("🔄 Kiểm tra", use_container_width=True):
            try:
                health_url = f"{st.session_state.get('api_url')}/health"
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    st.markdown('<div class="status-badge status-online">🟢 Kết nối OK</div>', 
                              unsafe_allow_html=True)
                    with st.expander("📊 Chi tiết"):
                        st.json(response.json())
                else:
                    st.markdown('<div class="status-badge status-offline">🔴 Lỗi Server</div>', 
                              unsafe_allow_html=True)
            except Exception as e:
                st.markdown('<div class="status-badge status-offline">🔴 Mất kết nối</div>', 
                          unsafe_allow_html=True)
                st.error(f"Lỗi: {str(e)[:50]}")
    
    with col2:
        current_url = st.session_state.get("api_url", API_URL)
        if current_url.startswith("http"):
            st.success("✅")
        else:
            st.warning("⚠️")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Usage Guide
    st.subheader("📖 Hướng Dẫn")
    st.markdown("""
    **Bước 1:** Sao chép Ngrok URL từ Colab  
    **Bước 2:** Dán vào ô "Nhập URL từ Colab"  
    **Bước 3:** Click "Kiểm tra" để xác nhận  
    **Bước 4:** Hỏi câu hỏi về dinh dưỡng!
    
    **Ví dụ câu hỏi:**
    - "Ức gà bao nhiêu đạm?"
    - "Chuối vs táo cái nào ít calo?"
    - "Các loại rau xanh tốt nhất?"
    """)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Clear History
    st.subheader("🧹 Quản Lý")
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.success("✅ Đã xóa tất cả tin nhắn!")
    
    # Stats
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.subheader("📊 Thống Kê")
    message_count = len(st.session_state.messages)
    user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.metric("Tổng tin nhắn", message_count)
    st.metric("Câu hỏi của bạn", user_count)

# =====================================================
# 📱 MAIN CONTENT AREA
# =====================================================

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🥗 Hinne - Nutrition AI</h1>
    <p class="header-subtitle">Trợ lý dinh dưỡng thông minh | Tư vấn ăn uống khoa học</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# 💬 CHAT HISTORY
# =====================================================
st.markdown('<div class="chat-container" id="chat-box">', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem; color: #999;">
        <h3 style="font-size: 1.5rem; margin-bottom: 1rem;">👋 Chào bạn!</h3>
        <p>Tôi là Hinne, trợ lý dinh dưỡng AI của bạn.</p>
        <p style="margin-top: 1rem; font-size: 0.9rem;">Hãy đặt câu hỏi về dinh dưỡng, calo, đạm, béo...</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-icon">👤</div>
                <div class="message-content">
                    <strong>Bạn:</strong><br>
                    {message['content']}
                    <div class="message-time">{message.get('time', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif message["role"] == "assistant":
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="message-icon">🤖</div>
                <div class="message-content">
                    <strong>Hinne:</strong><br>
                    {message['content']}
                    <div class="message-time">{message.get('time', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif message["role"] == "error":
            st.markdown(f"""
            <div class="chat-message error-message">
                <div class="message-icon">⚠️</div>
                <div class="message-content">
                    {message['content']}
                    <div class="message-time">{message.get('time', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<script>
  (function(){
    const chat = document.getElementById('chat-box');
    if(chat){ chat.scrollTop = chat.scrollHeight; }
    const input = document.querySelector('input[placeholder="Ví dụ: Ức gà bao nhiêu đạm? • Chuối có bao nhiêu calo?"]');
    if(input){ input.focus(); }
  })();
</script>
""", unsafe_allow_html=True)

# =====================================================
# 📝 INPUT AREA (FIXED AT BOTTOM - minimal, professional)
# =====================================================
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form('chat_form', clear_on_submit=True):
    cols = st.columns([1, 0.18])
    with cols[0]:
        user_input = st.text_input('', placeholder='Ví dụ: Ức gà bao nhiêu đạm? • Chuối có bao nhiêu calo?', key='form_user_input', label_visibility='collapsed')
    with cols[1]:
        send_button = st.form_submit_button('Gửi')
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# 🔄 PROCESS MESSAGE
# =====================================================
if send_button and user_input:
    # Add user message
    current_time = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "time": current_time
    })
    
    # Show loading and fetch response
    with st.spinner("⏳ Hinne đang suy nghĩ..."):
        try:
            # Call API
            payload = {"query": user_input}
            ask_url = f"{st.session_state.get('api_url')}/ask"
            response = requests.post(
                ask_url,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    answer = result.get("answer", "Không có câu trả lời")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "time": datetime.now().strftime("%H:%M:%S")
                    })
                else:
                    error_msg = result.get("error", "Lỗi không xác định")
                    st.session_state.messages.append({
                        "role": "error",
                        "content": f"❌ {error_msg}",
                        "time": datetime.now().strftime("%H:%M:%S")
                    })
            else:
                st.session_state.messages.append({
                    "role": "error",
                    "content": f"❌ Lỗi API: {response.status_code}",
                    "time": datetime.now().strftime("%H:%M:%S")
                })
        
        except requests.exceptions.Timeout:
            st.session_state.messages.append({
                "role": "error",
                "content": "❌ Hết timeout - Colab chưa trả lời (>30s)",
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "error",
                "content": f"❌ Không kết nối được. Kiểm tra Ngrok URL!",
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        except Exception as e:
            st.session_state.messages.append({
                "role": "error",
                "content": f"❌ Lỗi: {str(e)[:100]}",
                "time": datetime.now().strftime("%H:%M:%S")
            })
    
    # Rerun to show new message and clear input
    st.rerun()

# =====================================================
# 📋 FOOTER
# =====================================================
st.markdown("""
<div class="footer-text">
    <hr style="margin: 2rem 0; border: none; border-top: 1px solid #eee;">
    🔗 API: Colab + Ngrok + Local &nbsp;•&nbsp; 
    💾 Chat history lưu trong session &nbsp;•&nbsp; 
    ✨ Powered by LangChain RAG
</div>
""", unsafe_allow_html=True)
