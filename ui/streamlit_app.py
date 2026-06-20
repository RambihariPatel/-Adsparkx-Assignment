"""
NexaCloud Persona-Adaptive Customer Support Agent — Streamlit UI

A polished, dark-mode glassmorphism chat interface showcasing:
- Real-time persona detection with animated badges
- Source document citations with confidence scores
- Escalation status panel
- Conversation analytics sidebar
"""

import json
import os
import sys
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

# ── Page config must be FIRST Streamlit call ──────────────────
st.set_page_config(
    page_title="NexaCloud Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.config import config, validate_config
from app.persona_detector import get_detector
from app.rag_pipeline import get_pipeline
from app.response_generator import get_generator
from app.escalation_handler import get_handler
from app.conversation_memory import ConversationMemory

logging.basicConfig(level=logging.WARNING)

# ──────────────────────────────────────────────────────────────
# Custom CSS — Dark Glassmorphism
# ──────────────────────────────────────────────────────────────

CUSTOM_CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Reset ── */
* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.85) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(139, 92, 246, 0.2);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Main content area ── */
.main .block-container {
    padding: 1rem 2rem 2rem 2rem;
    max-width: 1200px;
}

/* ── Header ── */
.app-header {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.3), rgba(124, 58, 237, 0.3));
    border: 1px solid rgba(139, 92, 246, 0.4);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    gap: 16px;
}
.app-header h1 {
    color: #fff;
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.app-header p {
    color: #94a3b8;
    margin: 0;
    font-size: 0.85rem;
}

/* ── Chat Container ── */
.chat-container {
    background: rgba(15, 12, 41, 0.6);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 16px;
    padding: 20px;
    min-height: 420px;
    max-height: 560px;
    overflow-y: auto;
    margin-bottom: 16px;
    backdrop-filter: blur(12px);
}

/* ── Chat Bubbles ── */
.user-bubble {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 16px;
}
.user-bubble-inner {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 0.92rem;
    line-height: 1.5;
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.35);
}

.agent-bubble {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 16px;
    gap: 10px;
}
.agent-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.agent-bubble-inner {
    background: rgba(30, 27, 75, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.3);
    color: #e2e8f0;
    padding: 14px 18px;
    border-radius: 4px 18px 18px 18px;
    max-width: 75%;
    font-size: 0.92rem;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* ── Persona Badge ── */
.persona-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}
.badge-technical {
    background: rgba(6, 182, 212, 0.2);
    border: 1px solid rgba(6, 182, 212, 0.5);
    color: #22d3ee;
}
.badge-frustrated {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.5);
    color: #f87171;
}
.badge-executive {
    background: rgba(234, 179, 8, 0.2);
    border: 1px solid rgba(234, 179, 8, 0.5);
    color: #fbbf24;
}

/* ── Source Pills ── */
.source-container {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.source-pill {
    background: rgba(79, 70, 229, 0.2);
    border: 1px solid rgba(79, 70, 229, 0.4);
    color: #a5b4fc;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
}
.score-label {
    color: #64748b;
    font-size: 0.7rem;
    margin-top: 4px;
}

/* ── Escalation Panel ── */
.escalation-panel {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-left: 4px solid #ef4444;
    border-radius: 12px;
    padding: 18px;
    margin: 16px 0;
    backdrop-filter: blur(8px);
}
.escalation-panel h3 {
    color: #f87171;
    margin: 0 0 10px 0;
    font-size: 1rem;
}

/* ── Stat cards ── */
.stat-card {
    background: rgba(30, 27, 75, 0.7);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    margin-bottom: 12px;
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label {
    color: #64748b;
    font-size: 0.78rem;
    margin-top: 2px;
}

/* ── Input area ── */
.stTextInput > div > div {
    background: rgba(30, 27, 75, 0.8) !important;
    border: 1px solid rgba(139, 92, 246, 0.4) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}
.stTextInput input {
    color: #e2e8f0 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4) !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: rgba(30, 27, 75, 0.6) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 8px !important;
    color: #a5b4fc !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(30, 27, 75, 0.7);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 10px;
    padding: 12px;
}

/* ── Markdown text ── */
.stMarkdown p, .stMarkdown li { color: #cbd5e1; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #a5b4fc; }
.stMarkdown code {
    background: rgba(79, 70, 229, 0.2);
    color: #38bdf8;
    border-radius: 4px;
    padding: 2px 6px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(15, 12, 41, 0.3); }
::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.5);
    border-radius: 3px;
}

/* ── Typing indicator ── */
.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 12px 18px;
    background: rgba(30, 27, 75, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 4px 18px 18px 18px;
    width: fit-content;
    margin-bottom: 16px;
}
.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #7c3aed;
    animation: bounce 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.15s; }
.typing-dot:nth-child(3) { animation-delay: 0.3s; }
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}
</style>
"""


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

PERSONA_ICONS = {
    "Technical Expert": "⚙️",
    "Frustrated User": "😤",
    "Business Executive": "💼",
}

PERSONA_BADGE_CLASS = {
    "Technical Expert": "badge-technical",
    "Frustrated User": "badge-frustrated",
    "Business Executive": "badge-executive",
}


def render_persona_badge(persona: str, confidence: float) -> str:
    icon = PERSONA_ICONS.get(persona, "👤")
    badge_cls = PERSONA_BADGE_CLASS.get(persona, "badge-technical")
    conf_pct = int(confidence * 100)
    return (
        f'<span class="persona-badge {badge_cls}">'
        f'{icon} {persona} · {conf_pct}%'
        f'</span>'
    )


def render_sources(sources: list[str], score: float) -> str:
    if not sources:
        return ""
    pills = "".join(
        f'<span class="source-pill">📄 {s}</span>' for s in sources
    )
    return (
        f'<div class="source-container">{pills}</div>'
        f'<div class="score-label">Retrieval confidence: {score:.0%}</div>'
    )


def init_session_state():
    """Initialize all session state variables."""
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationMemory(window_size=config.memory_window)
    if "messages" not in st.session_state:
        st.session_state.messages = []  # List of display messages
    if "escalated" not in st.session_state:
        st.session_state.escalated = False
    if "handoff_summary" not in st.session_state:
        st.session_state.handoff_summary = None
    if "pipeline_ready" not in st.session_state:
        st.session_state.pipeline_ready = False
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0
    if "persona_history" not in st.session_state:
        st.session_state.persona_history = []


@st.cache_resource(show_spinner=False)
def load_pipeline():
    """Load the RAG pipeline (cached across sessions)."""
    pipeline = get_pipeline()
    if not pipeline.is_ready():
        return pipeline, False
    return pipeline, True


@st.cache_resource(show_spinner=False)
def load_agent_components():
    """Load detector, generator, handler (cached)."""
    return get_detector(), get_generator(), get_handler()


# ──────────────────────────────────────────────────────────────
# Main App
# ──────────────────────────────────────────────────────────────

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_session_state()

    # ── Validate API config ──────────────────────────────────
    is_valid, issues = validate_config()
    if not is_valid:
        st.error("⚠️ **Configuration Required**")
        for issue in issues:
            st.warning(issue)
        st.info(
            "Create a `.env` file with your `GOOGLE_API_KEY=...` and restart. "
            "Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey)"
        )
        st.stop()

    # ── Load components ──────────────────────────────────────
    with st.spinner("⚡ Loading AI components..."):
        pipeline, pipeline_ready = load_pipeline()
        detector, generator, handler = load_agent_components()

    st.session_state.pipeline_ready = pipeline_ready

    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div class="app-header">
        <div style="font-size:2.5rem">🤖</div>
        <div>
            <h1>NexaCloud Support Agent</h1>
            <p>Persona-Adaptive AI • Powered by Gemini • RAG-grounded responses</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🧠 Session Analytics")
        st.divider()

        # Persona indicator
        if st.session_state.persona_history:
            current_persona = st.session_state.persona_history[-1]["persona"]
            icon = PERSONA_ICONS.get(current_persona, "👤")
            st.markdown(f"**Detected Persona**")
            st.markdown(f"### {icon} {current_persona}")

            # Confidence gauge
            conf = st.session_state.persona_history[-1]["confidence"]
            st.progress(conf, text=f"Confidence: {conf:.0%}")
        else:
            st.markdown("**Persona:** Not yet detected")

        st.divider()

        # Stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", st.session_state.total_queries)
        with col2:
            st.metric(
                "Escalated",
                "🚨 YES" if st.session_state.escalated else "✅ NO"
            )

        if st.session_state.memory.total_user_turns > 0:
            st.metric("Turn #", st.session_state.memory.total_user_turns)
            top_score = 0.0
            for turn in reversed(st.session_state.memory.turns):
                if turn.role == "assistant" and turn.retrieval_score > 0:
                    top_score = turn.retrieval_score
                    break
            if top_score > 0:
                st.metric("Last Retrieval Score", f"{top_score:.0%}")

        st.divider()

        # Persona distribution
        if len(st.session_state.persona_history) > 1:
            st.markdown("**Persona History**")
            persona_counts = {}
            for p in st.session_state.persona_history:
                name = p["persona"]
                persona_counts[name] = persona_counts.get(name, 0) + 1
            for persona, count in persona_counts.items():
                icon = PERSONA_ICONS.get(persona, "👤")
                st.markdown(f"{icon} {persona}: **{count}x**")
            st.divider()

        # KB status
        if pipeline_ready:
            st.success("📚 Knowledge Base: Ready")
        else:
            st.error("📚 Knowledge Base: Not ingested")
            if st.button("🔄 Ingest Documents"):
                with st.spinner("Ingesting documents..."):
                    try:
                        stats = pipeline.ingest()
                        st.success(
                            f"✅ Ingested {stats['chunks_created']} chunks "
                            f"from {stats['documents_loaded']} documents!"
                        )
                        st.session_state.pipeline_ready = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ingestion failed: {e}")

        st.divider()

        # Example queries
        st.markdown("**💡 Try These Queries**")
        example_queries = [
            "⚙️ API auth 401 error — what's causing it?",
            "😤 I've tried everything and nothing works! HELP!",
            "💼 What's the business impact and resolution timeline?",
            "How do I reset my password?",
            "Explain the rate limiting policy",
        ]
        for q in example_queries:
            if st.button(q, key=f"ex_{q[:20]}", use_container_width=True):
                # Inject the query
                clean_q = q.split(" ", 1)[1] if q[0] in "⚙️😤💼" else q
                st.session_state["injected_query"] = clean_q
                st.rerun()

        st.divider()

        # Reset
        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.memory.clear()
            st.session_state.escalated = False
            st.session_state.handoff_summary = None
            st.session_state.total_queries = 0
            st.session_state.persona_history = []
            st.rerun()

        st.markdown(
            "<div style='color:#475569;font-size:0.75rem;margin-top:20px;'>"
            "NexaCloud Support Agent v1.0<br>"
            "Powered by Google Gemini + ChromaDB"
            "</div>",
            unsafe_allow_html=True
        )

    # ── Main Chat Area ────────────────────────────────────────

    # KB not ready warning
    if not pipeline_ready:
        st.warning(
            "⚠️ **Knowledge base not loaded.** "
            "Click **'Ingest Documents'** in the sidebar first, or run `python ingest.py` in terminal."
        )

    # Chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-bubble">'
                    f'<div class="user-bubble-inner">👤 {msg["content"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                # Agent message
                badge_html = ""
                if msg.get("persona"):
                    badge_html = render_persona_badge(msg["persona"], msg.get("confidence", 0.0))

                sources_html = ""
                if msg.get("sources"):
                    sources_html = render_sources(msg["sources"], msg.get("retrieval_score", 0.0))

                content_html = msg["content"].replace("\n", "<br>")

                st.markdown(
                    f'<div class="agent-bubble">'
                    f'<div class="agent-avatar">🤖</div>'
                    f'<div class="agent-bubble-inner">'
                    f'{badge_html}<br>'
                    f'{content_html}'
                    f'{sources_html}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        # Escalation panel
        if st.session_state.escalated and st.session_state.handoff_summary:
            summary = st.session_state.handoff_summary
            st.markdown(
                f'<div class="escalation-panel">'
                f'<h3>🚨 Escalated to Human Agent</h3>'
                f'<strong>Priority:</strong> {summary.get("priority", "P2")} &nbsp;|&nbsp; '
                f'<strong>Route to:</strong> {summary.get("route_to", "Support Team")}'
                f'</div>',
                unsafe_allow_html=True
            )

            with st.expander("📋 View Full Handoff Summary", expanded=False):
                st.markdown(handler.format_handoff_for_display(summary))
                st.json(summary)

    # ── Input Area ────────────────────────────────────────────
    st.divider()

    # Check for injected query (from sidebar buttons)
    injected = st.session_state.pop("injected_query", None)

    with st.form(key="chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "Message",
                value=injected or "",
                placeholder="Ask anything about NexaCloud — billing, API, account, troubleshooting...",
                label_visibility="collapsed",
                key="user_input_field",
            )
        with col_btn:
            submitted = st.form_submit_button("Send ➤", use_container_width=True)

    if submitted and user_input.strip():
        process_message(user_input.strip(), pipeline, detector, generator, handler)

    # Disabled state when escalated
    if st.session_state.escalated:
        st.info(
            "💬 This conversation has been escalated. "
            "A human agent will contact you shortly. "
            "Click **'New Conversation'** to start fresh."
        )


def process_message(
    user_input: str,
    pipeline,
    detector,
    generator,
    handler,
):
    """Process a user message through the full agent pipeline."""

    # 1. Add user message to display
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.total_queries += 1

    # 2. Detect persona
    memory: ConversationMemory = st.session_state.memory
    persona_result = detector.detect(
        message=user_input,
        conversation_history=memory.get_windowed_history(),
    )

    # Detect negative sentiment for memory tracking
    is_negative = persona_result.persona == "Frustrated User"

    memory.add_user_turn(
        content=user_input,
        persona=persona_result.persona,
        persona_confidence=persona_result.confidence,
        sentiment_negative=is_negative,
    )

    st.session_state.persona_history.append({
        "persona": persona_result.persona,
        "confidence": persona_result.confidence,
    })

    # 3. Retrieve relevant context
    rag_response = pipeline.retrieve(user_input)

    # 4. Check for escalation BEFORE generating response
    escalation = handler.evaluate(
        user_message=user_input,
        rag_response=rag_response,
        memory=memory,
    )

    if escalation.should_escalate:
        # Generate handoff summary
        handoff = handler.generate_handoff_summary(
            escalation_decision=escalation,
            memory=memory,
            current_user_message=user_input,
        )

        agent_content = (
            f"**{escalation.reason}**\n\n"
            f"📋 A handoff summary has been prepared for your assigned agent "
            f"(see below). They'll have full context of our conversation."
        )

        memory.add_assistant_turn(
            content=agent_content,
            sources=[],
            retrieval_score=0.0,
            escalated=True,
            escalation_reason=escalation.trigger_code,
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": agent_content,
            "persona": persona_result.persona,
            "confidence": persona_result.confidence,
            "sources": [],
            "retrieval_score": 0.0,
            "escalated": True,
        })

        st.session_state.escalated = True
        st.session_state.handoff_summary = handoff
        st.rerun()
        return

    # 5. Generate persona-adapted response
    agent_resp = generator.generate(
        persona=persona_result.persona,
        user_message=user_input,
        rag_response=rag_response,
        conversation_history=memory.get_windowed_history(),
    )

    # 6. Check escalation again after generation (grounding check)
    post_gen_escalation = handler.evaluate(
        user_message=user_input,
        rag_response=rag_response,
        memory=memory,
        agent_response_grounded=agent_resp.is_grounded,
    )

    memory.add_assistant_turn(
        content=agent_resp.content,
        sources=agent_resp.sources,
        retrieval_score=agent_resp.top_retrieval_score,
        escalated=post_gen_escalation.should_escalate,
        escalation_reason=post_gen_escalation.trigger_code if post_gen_escalation.should_escalate else None,
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": agent_resp.content,
        "persona": persona_result.persona,
        "confidence": persona_result.confidence,
        "sources": agent_resp.sources,
        "retrieval_score": agent_resp.top_retrieval_score,
        "escalated": False,
    })

    if post_gen_escalation.should_escalate:
        handoff = handler.generate_handoff_summary(
            escalation_decision=post_gen_escalation,
            memory=memory,
            current_user_message=user_input,
        )
        st.session_state.escalated = True
        st.session_state.handoff_summary = handoff

    st.rerun()


if __name__ == "__main__":
    main()
