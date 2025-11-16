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
    /* Main container */
    .main {
        padding: 0 !important;
    }
    
    /* Remove top padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 0;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.95;
        margin-top: 0.5rem;
    }
    
    /* Chat messages container */
    .chat-container {
        max-height: calc(100vh - 400px);
        overflow-y: auto;
        padding: 1.5rem 0;
        scroll-behavior: smooth;
    }
    
    /* Message styling */
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        gap: 0.75rem;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 4px solid #667eea;
        margin-left: 2rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-left: 4px solid #f5576c;
        margin-right: 2rem;
        box-shadow: 0 2px 8px rgba(245, 87, 108, 0.2);
    }
    
    .error-message {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        border-left: 4px solid #ff6b6b;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.2);
    }
    
    .message-icon {
        font-size: 1.5rem;
        min-width: 2rem;
        text-align: center;
    }
    
    .message-content {
        flex: 1;
        line-height: 1.6;
    }
    
    .message-time {
        font-size: 0.75rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    
    /* Input area - FOLLOWS SCROLL (relative, not fixed) */
    .input-container {
        position: relative;
        background: linear-gradient(to bottom, rgba(255,255,255,0.95) 0%, white 100%);
        padding: 1.5rem 1rem;
        margin-top: 2rem;
        border-top: 2px solid #e0e0e0;
        box-shadow: 0 -4px 15px rgba(0,0,0,0.08);
        border-radius: 12px 12px 0 0;
    }
    
    @media (max-width: 768px) {
        .input-container {
            padding: 1rem 0.75rem;
            margin-top: 1rem;
        }
    }
    
    /* Form styling */
    .form-input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .form-input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .status-online {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-offline {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Divider */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 1.5rem 0;
    }
    
    /* Footer text */
    .footer-text {
        text-align: center;
        font-size: 0.875rem;
        color: #999;
        margin-top: 2rem;
    }
    
    /* Loading spinner */
    .loading-text {
        text-align: center;
        color: #667eea;
        font-weight: 600;
    }
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
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

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

# =====================================================
# 📝 INPUT AREA (FOLLOWS SCROLL)
# =====================================================

st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Input form
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.92, 0.08], gap="small")
    
    with col1:
        user_input = st.text_input(
            "💭 Hỏi tôi gì đó...",
            placeholder="Ví dụ: Ức gà bao nhiêu đạm? • Chuối có bao nhiêu calo?",
            key="form_user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.form_submit_button("📤", use_container_width=True)

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
