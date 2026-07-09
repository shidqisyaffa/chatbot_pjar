import uuid
import streamlit as st

# Configure page metadata first before any other Streamlit commands
st.set_page_config(
    page_title="Network Programming Academic Chatbot",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

import config
import database
import models
from utils.helpers import get_uptime_string, get_client_info
from services import history_service, logging_service, chat_service
from services.llm_service import check_llm_status
from services.prompts import SUGGESTED_QUESTIONS, REJECTION_MESSAGE
from database import check_db_status

# -------------------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------------------
db_error = False
if config.DATABASE_URL:
    db_initialized = database.init_db()
    if not db_initialized:
        db_error = True
else:
    db_error = True

# -------------------------------------------------------------
# APPLICATION SESSION STATE SETUP
# -------------------------------------------------------------
if "session_uuid" not in st.session_state:
    st.session_state.session_uuid = str(uuid.uuid4())

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# Ensure the active session is stored in the database
user_agent, ip_address = get_client_info()
if not db_error:
    history_service.create_session(
        session_uuid=st.session_state.session_uuid,
        user_agent=user_agent,
        ip_address=ip_address
    )

# -------------------------------------------------------------
# LOAD STYLESHEET
# -------------------------------------------------------------
try:
    with open("assets/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# -------------------------------------------------------------
# SIDEBAR DEVELOPMENT
# -------------------------------------------------------------
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #3b82f6;'>🔌 PJAR Chatbot</h2>",
    unsafe_allow_html=True
)

# 1. Connection Status Component
st.sidebar.markdown("### 🌐 Connection Status")
db_connected = check_db_status() if not db_error else False
llm_connected, active_model = check_llm_status()

db_pill = '<span class="status-pill status-connected">🟢 Connected</span>' if db_connected else '<span class="status-pill status-disconnected">🔴 Disconnected</span>'
llm_pill = '<span class="status-pill status-connected">🟢 Connected</span>' if llm_connected else '<span class="status-pill status-disconnected">🔴 Disconnected</span>'

status_html = f"""
<div class="status-container">
    <div class="status-row">
        <span class="status-label">Neon DB:</span>
        <span class="status-value">{db_pill}</span>
    </div>
    <div class="status-row">
        <span class="status-label">LM Studio:</span>
        <span class="status-value">{llm_pill}</span>
    </div>
    <div class="status-row" style="margin-top: 5px; font-size: 0.75rem;">
        <span class="status-label" style="color: #94a3b8;">Active Model:</span>
        <span style="font-weight: 500; color: #3b82f6;">{active_model if llm_connected else 'N/A'}</span>
    </div>
    <div class="status-row" style="font-size: 0.75rem;">
        <span class="status-label" style="color: #94a3b8;">Server Uptime:</span>
        <span style="font-weight: 500; color: #cbd5e1;">{get_uptime_string()}</span>
    </div>
</div>
"""
st.sidebar.markdown(status_html, unsafe_allow_html=True)

# Warning notifications if services are offline
if not db_connected:
    st.sidebar.warning("⚠️ Neon Database connection offline. History & monitoring will not save correctly.")
if not llm_connected:
    st.sidebar.error("🔴 LM Studio or ngrok tunnel offline. AI responses are currently unavailable.")

# 2. Network Monitoring Dashboard Component
st.sidebar.markdown("### 📊 Network Monitoring")
metrics = logging_service.get_logs_summary() if db_connected else {
    "total_sessions": 0, "total_requests": 0, "total_responses": 0,
    "avg_response_time_ms": 0, "today_chats": 0, "request_success": 0, "request_failed": 0
}

metrics_html = f"""
<div class="monitoring-grid">
    <div class="monitoring-card">
        <div class="monitoring-title">Total Sessions</div>
        <div class="monitoring-value">{metrics["total_sessions"]}</div>
    </div>
    <div class="monitoring-card">
        <div class="monitoring-title">Today's Chat</div>
        <div class="monitoring-value">{metrics["today_chats"]}</div>
    </div>
    <div class="monitoring-card">
        <div class="monitoring-title">Req/Resp Log</div>
        <div class="monitoring-value">{metrics["total_requests"]}</div>
    </div>
    <div class="monitoring-card">
        <div class="monitoring-title">Avg Latency</div>
        <div class="monitoring-value" style="font-size: 1.1rem; padding-top: 5px;">{metrics["avg_response_time_ms"]} ms</div>
    </div>
    <div class="monitoring-card" style="grid-column: span 2;">
        <div class="monitoring-title">Logs Status (Success / Fail)</div>
        <div class="monitoring-value" style="font-size: 1.1rem; color: #10b981;">
            🟢 {metrics["request_success"]} <span style="color: #94a3b8;">/</span> 🔴 {metrics["request_failed"]}
        </div>
    </div>
</div>
"""
st.sidebar.markdown(metrics_html, unsafe_allow_html=True)

# 3. Chat Session Navigation & History
st.sidebar.markdown("### 💬 Chat History")

# New Chat Handler
if st.sidebar.button("➕ New Chat", use_container_width=True):
    new_uuid = str(uuid.uuid4())
    st.session_state.session_uuid = new_uuid
    if db_connected:
        history_service.create_session(new_uuid, user_agent, ip_address)
    st.rerun()

# Retrieve list of previous sessions
sessions = history_service.list_sessions() if db_connected else []
if not sessions:
    st.sidebar.caption("No chat history available.")
else:
    active_uuid = st.session_state.session_uuid
    
    # Calculate index of currently active session
    session_uuids = [s["session_uuid"] for s in sessions]
    try:
        active_idx = session_uuids.index(active_uuid)
    except ValueError:
        active_idx = 0
        if session_uuids:
            st.session_state.session_uuid = session_uuids[0]
            
    # Format labels for session select dropdown
    session_options = []
    for s in sessions:
        lbl = f"Session {s['session_uuid'][:8]}... ({s['updated_at'].strftime('%d %b %H:%M')})"
        session_options.append(lbl)
        
    if session_uuids:
        selected_lbl = st.sidebar.selectbox(
            "Select Session",
            options=session_options,
            index=active_idx,
            key="sess_selector"
        )
        # Update active uuid if changed
        selected_idx = session_options.index(selected_lbl)
        if session_uuids[selected_idx] != active_uuid:
            st.session_state.session_uuid = session_uuids[selected_idx]
            st.rerun()

# Deletion Controls
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🗑️ Delete Chat", use_container_width=True, disabled=not db_connected):
        if db_connected:
            history_service.delete_session(st.session_state.session_uuid)
            st.session_state.session_uuid = str(uuid.uuid4())
            st.toast("Active chat session deleted.")
            st.rerun()
with col2:
    if st.button("🚨 Delete All", use_container_width=True, disabled=not db_connected):
        if db_connected:
            history_service.delete_all_sessions()
            st.session_state.session_uuid = str(uuid.uuid4())
            st.toast("All chat sessions deleted.")
            st.rerun()

# About / Course Info Section
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About This Chatbot"):
    st.markdown("""
    **Chatbot Akademik Pemrograman Jaringan**
    
    Dirancang khusus untuk membantu mahasiswa dalam materi mata kuliah **Pemrograman Jaringan (PJAR)**.
    
    **Dual Domain Validation:**
    * **Layer 1:** Keyword Validation memeriksa relevansi prompt sebelum dikirim ke AI model.
    * **Layer 2:** System Instructions melatih AI menolak topik non-akademik di luar mata kuliah.
    
    *Dibuat untuk Tugas Besar / UAS.*
    """)

# -------------------------------------------------------------
# MAIN CHAT PANEL
# -------------------------------------------------------------
st.title("Academic Chatbot: Pemrograman Jaringan 🔌💻")
st.caption(f"Active Session UUID: `{st.session_state.session_uuid}`")

# Fetch and render current session message history
messages = history_service.get_messages(st.session_state.session_uuid) if db_connected else []

for msg in messages:
    role = msg["role"]
    avatar = "👤" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["message"])
        # Display timestamp
        timestamp_str = msg["created_at"].strftime("%H:%M")
        st.markdown(f'<div class="timestamp-label">🕒 {timestamp_str}</div>', unsafe_allow_html=True)

# Display Suggested Questions if conversation has no history
if len(messages) == 0:
    st.markdown("### Selamat Datang! 👋")
    st.markdown(
        "Saya adalah asisten AI akademik Anda untuk kuliah **Pemrograman Jaringan**. "
        "Silakan pilih topik di bawah ini atau tulis pertanyaan Anda langsung di kolom obrolan."
    )
    
    st.write("**Rekomendasi Pertanyaan:**")
    for sq in SUGGESTED_QUESTIONS:
        if st.button(sq, key=f"suggested_{sq}"):
            st.session_state.pending_question = sq
            st.rerun()

# Capture prompt input
user_prompt = st.chat_input("Tanyakan sesuatu tentang Pemrograman Jaringan...")

# Check if a recommended question was clicked
active_prompt = None
if user_prompt:
    active_prompt = user_prompt
elif st.session_state.pending_question:
    active_prompt = st.session_state.pending_question
    st.session_state.pending_question = None

# -------------------------------------------------------------
# CHAT LOGIC AND RESPONSE GENERATION
# -------------------------------------------------------------
if active_prompt:
    # 1. Render user prompt in UI
    with st.chat_message("user", avatar="👤"):
        st.markdown(active_prompt)
        
    # 2. Query chatbot flow and render streaming completion
    with st.chat_message("assistant", avatar="🤖"):
        # We pass active session messages as history context
        response_generator = chat_service.handle_chat_message(
            session_uuid=st.session_state.session_uuid,
            prompt=active_prompt,
            history=messages
        )
        
        # Stream response chunks to UI
        full_response = st.write_stream(response_generator)
        
    # Refresh to update session list and monitoring statistics
    st.rerun()
