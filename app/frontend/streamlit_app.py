"""
CareerBridge AI - Streamlit Frontend Application
Specialized for UN SDG 8: Decent Work & Economic Growth
"""
import os
import uuid
import datetime
import requests
import streamlit as st

# Configure page metadata
st.set_page_config(
    page_title="CareerBridge AI | SDG 8 Career Guide",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

# Custom Styling: Modern, clean, professional, minimal + premium + student-friendly
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header styles */
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #31102b 100%);
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(90deg, #ffffff, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.brand-subtitle {
    font-size: 0.88rem;
    color: #cbd5e1;
    margin-top: 0.2rem;
    font-weight: 500;
}

.sdg-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(162, 25, 66, 0.25);
    color: #ff6b8b;
    border: 1px solid rgba(244, 63, 94, 0.4);
    padding: 0.45rem 0.9rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    backdrop-filter: blur(8px);
}

/* Welcome Card */
.welcome-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(12px);
}

.welcome-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.75rem;
}

.welcome-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.5rem;
    margin: 1rem 0;
}

.welcome-item {
    font-size: 0.88rem;
    color: #cbd5e1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Readiness Snapshot Card */
.snapshot-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
    border: 1px solid rgba(162, 25, 66, 0.35);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.snapshot-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.snapshot-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: #f43f5e;
}

.snapshot-tag {
    font-size: 0.72rem;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    background: rgba(244, 63, 94, 0.15);
    color: #fda4af;
    font-weight: 600;
}

.progress-bar-bg {
    background: rgba(255, 255, 255, 0.1);
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.progress-bar-fill {
    background: linear-gradient(90deg, #f43f5e, #fb7185);
    height: 100%;
    border-radius: 4px;
}

.snapshot-disclaimer {
    font-size: 0.7rem;
    color: #94a3b8;
    margin-top: 0.75rem;
    font-style: italic;
}

/* Timestamp styling */
.msg-time {
    font-size: 0.68rem;
    color: #94a3b8;
    margin-top: 0.3rem;
}

/* Primary Button Styling */
div.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}
div.stButton > button:hover {
    border-color: #f43f5e;
    color: #f43f5e;
    transform: translateY(-1px);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "readiness_snapshot" not in st.session_state:
    st.session_state.readiness_snapshot = None

def reset_chat():
    """Resets conversational memory and generates a new session id."""
    old_session = st.session_state.session_id
    try:
        # Notify backend to clear memory
        requests.post(f"{BACKEND_URL}/reset", json={"session_id": old_session}, timeout=3.0)
    except Exception:
        # If backend is unavailable or direct, call backend memory directly
        try:
            from app.backend.memory import memory_store
            memory_store.reset_session(old_session)
        except Exception:
            pass

    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.readiness_snapshot = None

def send_chat_message(user_input: str):
    """Sends a chat message to backend or fallback engine and appends to UI state."""
    if not user_input.strip():
        return

    timestamp = datetime.datetime.now().strftime("%I:%M %p")
    # Append user message to UI state immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "time": timestamp
    })

    # Call backend API
    response_text = ""
    snapshot_data = None

    try:
        payload = {
            "message": user_input,
            "session_id": st.session_state.session_id
        }
        res = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=20.0)
        if res.status_code == 200:
            data = res.json()
            response_text = data.get("response", "")
            snapshot_data = data.get("readiness_snapshot")
        else:
            response_text = "AI response could not be generated. Please check the API configuration."
    except Exception:
        # Fallback to direct Python backend import if standalone
        try:
            from app.backend.chatbot import process_chat_message
            result = process_chat_message(st.session_state.session_id, user_input)
            response_text = result.get("response", "AI response could not be generated. Please check the API configuration.")
            snapshot_data = result.get("readiness_snapshot")
        except Exception:
            response_text = "AI response could not be generated. Please check the API configuration."

    asst_timestamp = datetime.datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "time": asst_timestamp
    })

    if snapshot_data:
        st.session_state.readiness_snapshot = snapshot_data

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Session & Tools")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        reset_chat()
        st.rerun()

    st.caption(f"Session ID: `{st.session_state.session_id[:8]}...`")

    st.markdown("---")

    # Innovation Feature: Career Readiness Snapshot
    st.markdown("### 📊 Career Readiness Snapshot")
    if st.session_state.readiness_snapshot:
        snap = st.session_state.readiness_snapshot
        pct = snap.get("estimated_readiness_pct", 0)
        stage = snap.get("current_stage", "Foundations")
        target = snap.get("target_role", "Tech Path")
        strengths = snap.get("current_strengths", [])
        next_skills = snap.get("recommended_next", [])

        st.markdown(f"""
        <div class="snapshot-card">
            <div class="snapshot-header">
                <span class="snapshot-title">{target}</span>
                <span class="snapshot-tag">{stage.split(':')[0]}</span>
            </div>
            <div style="font-size: 0.78rem; color: #cbd5e1;">Learning Readiness Progress: <b>{pct}%</b></div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: {pct}%;"></div>
            </div>
            <div style="font-size: 0.75rem; margin-top: 0.5rem; color: #e2e8f0;">
                <b>Identified Strengths:</b> {', '.join(strengths[:3]) if strengths else 'Under exploration'}
            </div>
            <div style="font-size: 0.75rem; margin-top: 0.3rem; color: #fda4af;">
                <b>Recommended Next:</b> {', '.join(next_skills[:3]) if next_skills else 'Continue current track'}
            </div>
            <div class="snapshot-disclaimer">
                ⚠️ {snap.get('disclaimer')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Your **Career Readiness Snapshot** will appear here as you share your education, skills, and target goals.")

    st.markdown("---")

    # SDG Impact Panel
    with st.expander("🌍 Why SDG 8?", expanded=False):
        st.markdown(
            "**CareerBridge AI** supports **UN SDG 8: Decent Work and Economic Growth** "
            "by helping users build job-relevant skills, improve employability, understand professional development, "
            "and make informed decisions related to decent work and sustainable economic participation."
        )

    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.75rem; color: #64748b; text-align: center;'>"
        "CareerBridge AI • Built for SDG 8 Competition<br>"
        "Ethical & Responsible Career Guidance"
        "</div>",
        unsafe_allow_html=True
    )

# --- MAIN SCREEN HEADER ---
st.markdown("""
<div class="header-container">
    <div>
        <h1 class="brand-title">CareerBridge AI</h1>
        <div class="brand-subtitle">Your AI Guide to Skills, Careers & Decent Work</div>
    </div>
    <div class="sdg-badge">
        <span>🌍</span>
        <span>SDG 8 • Decent Work & Economic Growth</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Welcome Screen (If no messages yet)
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-title">Hi! I'm CareerBridge AI 👋</div>
        <div style="color: #94a3b8; font-size: 0.92rem; margin-bottom: 0.75rem;">
            I can help you with your career exploration and skill development journey:
        </div>
        <div class="welcome-list">
            <div class="welcome-item">🎯 <span>Career planning & roadmaps</span></div>
            <div class="welcome-item">💻 <span>Skill gap identification</span></div>
            <div class="welcome-item">📄 <span>Resume improvement guidance</span></div>
            <div class="welcome-item">🎤 <span>Interactive mock interviews</span></div>
            <div class="welcome-item">🚀 <span>Internship & job readiness</span></div>
            <div class="welcome-item">🌱 <span>Professional workplace growth</span></div>
            <div class="welcome-item">🤝 <span>Decent-work awareness (SDG 8)</span></div>
        </div>
        <div style="font-size: 0.85rem; color: #cbd5e1; margin-top: 0.5rem;">
            Ask me anything related to your career journey or click an example below to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Prompt Cards
    st.markdown("##### 💡 Quick Start Prompts")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 Build me a career roadmap", use_container_width=True):
            send_chat_message("How do I build a structured career roadmap for my field of interest?")
            st.rerun()
        if st.button("🎤 Help me prepare for an interview", use_container_width=True):
            send_chat_message("How do I prepare for job and internship interviews?")
            st.rerun()
    with col2:
        if st.button("🌟 What are key employability skills?", use_container_width=True):
            send_chat_message("What are employability skills?")
            st.rerun()
        if st.button("📄 Review my resume", use_container_width=True):
            send_chat_message("How can I improve my resume to stand out to employers?")
            st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "time" in msg:
            st.markdown(f"<div class='msg-time'>{msg['time']}</div>", unsafe_allow_html=True)

# Chat Input Box
user_prompt = st.chat_input("Ask a question about careers, skills, roadmaps, or decent work...")
if user_prompt:
    send_chat_message(user_prompt)
    st.rerun()
