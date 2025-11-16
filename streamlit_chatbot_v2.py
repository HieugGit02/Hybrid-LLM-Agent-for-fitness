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
  :root {
    --bg: #f5f7fa;
    --card: #ffffff;
    --muted: #64748b;
    --accent: #3b82f6;
    --accent-dark: #1e40af;
    --border: #e2e8f0;
    --text: #0f172a;
  }
  
  * { box-sizing: border-box; }
  
  html, body {
    height: 100%;
    overflow: hidden;
  }
  
  .main {
    padding: 0 !important;
    background: var(--bg);
    height: 100vh;
    overflow: hidden;
  }
  
  /* Force sidebar to stay visible */
  [data-testid="stSidebar"] {
    background: var(--card);
    width: 280px !important;
    min-width: 280px !important;
  }
  
  [data-testid="stSidebar"][aria-expanded="false"] {
    display: flex !important;
    width: 280px !important;
  }
  
  .block-container {
    padding-top: 1.25rem;
    padding-bottom: 140px;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  /* Minimal header */
  .header-container {
    background: transparent;
    padding: 0 0 1rem 0;
    margin-bottom: 0.5rem;
    flex-shrink: 0;
  }
  
  .header-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text);
    margin: 0;
    letter-spacing: -0.5px;
  }
  
  .header-subtitle {
    color: var(--muted);
    margin-top: 0.25rem;
    font-size: 0.9rem;
    font-weight: 400;
  }
  
  /* Chat container - flexible, fills space */
  .chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem 0;
    scroll-behavior: smooth;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  
  /* Chat message bubbles - elegant & rounded */
  .chat-message {
    display: flex;
    margin: 0.6rem 0;
    gap: 0.5rem;
    padding: 0;
    animation: fadeIn 0.2s ease-in;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .user-message {
    justify-content: flex-end;
  }
  
  .user-message .message-content {
    background: var(--accent);
    color: white;
    padding: 0.8rem 1.1rem;
    border-radius: 18px;
    border-bottom-right-radius: 4px;
    max-width: 65%;
    word-wrap: break-word;
    box-shadow: 0 1px 3px rgba(59, 130, 246, 0.2);
    font-size: 0.95rem;
    line-height: 1.4;
  }
  
  .bot-message {
    justify-content: flex-start;
  }
  
  .bot-message .message-content {
    background: var(--card);
    color: var(--text);
    padding: 0.8rem 1.1rem;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    max-width: 65%;
    word-wrap: break-word;
    border: 1px solid var(--border);
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    font-size: 0.95rem;
    line-height: 1.4;
  }
  
  .error-message {
    justify-content: center;
  }
  
  .error-message .message-content {
    background: #fef2f2;
    color: #991b1b;
    padding: 0.8rem 1.1rem;
    border-radius: 8px;
    border-left: 3px solid #dc2626;
    max-width: 75%;
    font-size: 0.95rem;
  }
  
  .message-icon {
    font-size: 1.1rem;
    margin-top: 0.2rem;
    flex-shrink: 0;
  }
  
  .message-content {
    flex: 0 0 auto;
  }
  
  .message-time {
    font-size: 0.7rem;
    color: var(--muted);
    margin-top: 0.25rem;
    display: none;
  }
  
  /* Fixed input area */
  .input-container {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(180deg, var(--card) 0%, rgba(255, 255, 255, 0.98) 100%);
    padding: 12px 16px;
    border-top: 1px solid var(--border);
    box-shadow: 0 -2px 8px rgba(15, 23, 42, 0.06);
    z-index: 999;
  }
  
  /* Sidebar styling */
  [data-testid="stSidebar"] {
    border-right: 1px solid var(--border);
  }
  
  /* Scrollbar styling */
  .chat-container::-webkit-scrollbar {
    width: 6px;
  }
  
  .chat-container::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .chat-container::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
  }
  
  .chat-container::-webkit-scrollbar-thumb:hover {
    background: #cbd5e1;
  }
  
  /* Responsive */
  @media (max-width: 768px) {
    [data-testid="stSidebar"] {
      width: 250px !important;
      min-width: 250px !important;
    }
    
    .user-message .message-content,
    .bot-message .message-content {
      max-width: 80%;
    }
  }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 📊 SIDEBAR - MINIMAL (Only API config)
# =====================================================
with st.sidebar:
    st.title("⚙️ Cài Đặt")
    
    # API URL Configuration
    api_input = st.text_input(
        "Ngrok URL:",
        value=st.session_state.get("api_url", API_URL),
        placeholder="https://xxxxx.ngrok-free.app"
    )
    
    if api_input and api_input != st.session_state.get("api_url"):
        new_url = api_input.rstrip('/')
        st.session_state["api_url"] = new_url
        st.success("✅ Đã cập nhật")
    
    # Health Check
    if st.button("🔄 Kiểm tra kết nối", use_container_width=True):
        try:
            health_url = f"{st.session_state.get('api_url')}/health"
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                st.success("🟢 Kết nối OK")
            else:
                st.error("🔴 Lỗi Server")
        except Exception as e:
            st.error("🔴 Mất kết nối")

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
                <div class="message-content">
                    {message['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif message["role"] == "assistant":
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="message-icon">🤖</div>
                <div class="message-content">
                    {message['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif message["role"] == "error":
            st.markdown(f"""
            <div class="chat-message error-message">
                <div class="message-content">
                    {message['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<script>
  (function(){
    const chat = document.getElementById('chat-box');
    if(chat){ setTimeout(() => { chat.scrollTop = chat.scrollHeight; }, 100); }
    setTimeout(() => {
      const inputs = document.querySelectorAll('input[type="text"]');
      if(inputs.length > 0) inputs[inputs.length - 1].focus();
    }, 50);
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
