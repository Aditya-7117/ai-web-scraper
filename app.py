import streamlit as st
import os

from backend.parser import WebParser
from backend.gemini_handler import GeminiHandler
from backend.rag.rag_engine import RAGEngine
from backend.archive.wayback_analyzer import WaybackAnalyzer
from backend.ui import section_title, badge


# =========================
# Page configuration
# =========================
st.set_page_config(
    page_title="AI Web Scraper & Analyzer",
    page_icon="🔍",
    layout="wide"
)

# =========================
# UI / DESIGN SYSTEM
# =========================
st.markdown("""
<style>

/* ===== Background ===== */
.stApp {
    background:
        radial-gradient(1200px 600px at 20% 0%, rgba(59,130,246,0.28), transparent 60%),
        radial-gradient(900px 500px at 80% 20%, rgba(14,165,233,0.22), transparent 55%),
        linear-gradient(180deg, #020617 0%, #020617 100%);
    color: #e5e7eb;
    font-family: 'Inter', system-ui, sans-serif;
}

/* ===== Hero ===== */
.main-header {
    font-size: 3.2rem;
    font-weight: 900;
    text-align: center;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #93c5fd, #38bdf8, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-header {
    text-align: center;
    color: #9ca3af;
    font-size: 1.1rem;
    margin: 0.6rem 0 3rem 0;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #020617);
    border-right: 1px solid #1e293b;
}

/* ===== Inputs ===== */
input, textarea, select {
    background-color: rgba(2,6,23,0.95) !important;
    border: 1px solid #1e293b !important;
    border-radius: 10px !important;
    color: #e5e7eb !important;
}

/* ===== Buttons ===== */
.stButton>button {
    background: linear-gradient(90deg, #2563eb, #0ea5e9);
    color: white;
    border-radius: 12px;
    padding: 0.7rem 1.1rem;
    font-weight: 700;
    border: none;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px rgba(56,189,248,0.35);
}

/* ===== Cards ===== */
.card {
    background: linear-gradient(180deg, rgba(15,23,42,0.9), rgba(2,6,23,0.9));
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 18px 35px rgba(0,0,0,0.4);
    transition: all 0.35s ease;
}

.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 35px 60px rgba(0,0,0,0.55);
    border-color: #38bdf8;
}

/* ===== Badges ===== */
.badge-chip {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    background: rgba(59,130,246,0.2);
    border: 1px solid #3b82f6;
    margin-right: 0.5rem;
}

/* ===== Status Boxes ===== */
.success-box {
    background: rgba(16,185,129,0.12);
    border-left: 4px solid #10b981;
    padding: 1rem;
    border-radius: 10px;
}
.error-box {
    background: rgba(239,68,68,0.12);
    border-left: 4px solid #ef4444;
    padding: 1rem;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# Session State
# =========================
if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = None
if "gemini_handler" not in st.session_state:
    st.session_state.gemini_handler = None
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None
if "wayback" not in st.session_state:
    st.session_state.wayback = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# HERO
# =========================
st.markdown(
    f"<div class='main-header'>🔍 AI Web Scraper & Analyzer {badge('v5')}</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='sub-header'>Scrape websites • Ground answers • Analyze history</div>",
    unsafe_allow_html=True
)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Control Panel")

    api_key = st.text_input(
        "LLM API Key",
        value=os.getenv("LLM_API_KEY", ""),
        placeholder="Gemini / OpenAI / Groq API Key",
        type="password"
    )

    st.divider()

    st.subheader("Scraping Options")
    use_selenium = st.checkbox("Use Selenium (dynamic sites)", value=False)
    use_archives = st.checkbox("Enable Web Archive Analysis", value=False)

    st.subheader("Capabilities")
    st.markdown("""
    • Static & dynamic scraping  
    • RAG with hyperlinks  
    • AI summaries & Q&A  
    • Historical website analysis  
    """)

    if st.session_state.scraped_data:
        if st.button("Clear Session"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# =========================
# URL INPUT
# =========================
col1, col2 = st.columns([2, 1])
with col1:
    url = st.text_input("🌐 Website URL", placeholder="https://example.com")
with col2:
    st.write("")
    scrape_button = st.button("🚀 Scrape Website", use_container_width=True)

# =========================
# SCRAPING
# =========================
if scrape_button and url:
    with st.spinner("Scraping website..."):
        parser = WebParser()
        result = parser.scrape(url, use_selenium=use_selenium)

        if result["success"]:
            st.session_state.scraped_data = result
            st.session_state.rag_engine = RAGEngine(result["content"], result["links"])
            st.session_state.wayback = WaybackAnalyzer(url)

            if api_key:
                st.session_state.gemini_handler = GeminiHandler(api_key)
                st.session_state.gemini_handler.set_context(
                    result["content"],
                    result["title"],
                    result["description"]
                )

            st.markdown(
                f"<div class='success-box'>Scraped successfully using {result['method']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='error-box'>Error: {result['error']}</div>",
                unsafe_allow_html=True
            )

# =========================
# MAIN CONTENT
# =========================
if st.session_state.scraped_data:
    data = st.session_state.scraped_data

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📄 Content", "🤖 AI Analysis", "💬 Chat (RAG + Links)", "🕰️ Web Archives"]
    )

    with tab1:
        st.markdown(
            f"<div class='card'><b>{data['title']}</b><br/>{data['description']}</div>",
            unsafe_allow_html=True
        )
        st.text_area("Content", data["content"], height=400)

    with tab2:
        if st.session_state.gemini_handler:
            if st.button("📝 Generate Summary"):
                st.write(st.session_state.gemini_handler.summarize()["response"])
        else:
            st.info("Provide an LLM API key to enable AI analysis.")

    with tab3:
        question = st.chat_input("Ask a question about this website...")
        if question:
            rag = st.session_state.rag_engine
            rag_result = rag.build_answer(question)

            if rag_result["success"]:
                st.markdown("### ✅ Answer")
                st.write(rag_result["answer"])

                if rag_result["sources"]:
                    st.markdown("### 🔗 Sources")
                    for src in rag_result["sources"]:
                        st.markdown(f"- [{src['text']}]({src['url']})")
            else:
                st.warning("No relevant grounded information found.")

    with tab4:
        st.subheader("Historical Website Analysis")

        if not use_archives:
            st.info("Enable Web Archive Analysis from the sidebar.")
        else:
            years = st.multiselect(
                "Select years to compare",
                options=[2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
                default=[2019, 2024]
            )

            if st.button("Analyze History"):
                with st.spinner("Fetching historical snapshots..."):
                    result = st.session_state.wayback.analyze(years)

                    if result["success"]:
                        st.success(
                            f"Comparing {result['from_year']} → {result['to_year']}"
                        )

                        st.markdown("### 🟢 Emerging Focus Areas")
                        st.write(", ".join(result["new_focus_terms"][:20]))

                        st.markdown("### 🔴 Reduced Focus Areas")
                        st.write(", ".join(result["deprecated_terms"][:20]))
                    else:
                        st.error(result["error"])

# =========================
# HOME
# =========================
else:
    st.markdown(section_title("🚀 What this platform does"), unsafe_allow_html=True)
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1.6rem;">
        <div class="card"><b>🔍 Universal Scraping</b><br/>Static & dynamic websites</div>
        <div class="card"><b>📚 RAG with Sources</b><br/>Answers with direct hyperlinks</div>
        <div class="card"><b>🧠 AI Analysis</b><br/>Summaries & insights</div>
        <div class="card"><b>🕰️ Web Archives</b><br/>Historical trend comparison</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.divider()
st.markdown(
    "<div style='text-align:center;color:#64748b;font-size:0.9rem;'>"
    "AI Web Scraper • RAG + Web Archives • Final Complete Version"
    "</div>",
    unsafe_allow_html=True
)
