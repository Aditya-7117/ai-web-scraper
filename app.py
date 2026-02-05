import streamlit as st
from backend.parser import WebParser
from backend.gemini_handler import GeminiHandler
import os

# =========================
# Page configuration
# =========================
st.set_page_config(
    page_title="AI Web Scraper & Analyzer",
    page_icon="🔍",
    layout="wide"
)

# =========================
# Custom CSS (Dark Enterprise Theme)
# =========================
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #e6e6e6;
}
.main-header {
    font-size: 2.6rem;
    font-weight: 700;
    text-align: center;
    color: #4da3ff;
}
.sub-header {
    text-align: center;
    color: #9aa4b2;
    margin-bottom: 2rem;
}
.success-box {
    background-color: #0f5132;
    border-left: 4px solid #2ecc71;
    padding: 1rem;
}
.error-box {
    background-color: #842029;
    border-left: 4px solid #ff4d4f;
    padding: 1rem;
}
.info-box {
    background-color: #0d3b66;
    border-left: 4px solid #4da3ff;
    padding: 1rem;
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
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# Header
# =========================
st.markdown('<div class="main-header">🔍 AI Web Scraper & Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Scrape any website, analyze it with AI, and explore insights</div>',
    unsafe_allow_html=True
)

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        placeholder="Enter your Gemini API key",
        type="password"
    )

    st.divider()

    st.header("📋 Scraping Options")
    use_selenium = st.checkbox(
        "Use Selenium (dynamic sites)",
        value=False
    )

    domain_mode = st.selectbox(
        "Domain Mode",
        ["Auto", "E-commerce", "Real Estate", "News", "Generic"],
        help="Select domain-specific scraping behavior"
    )

    use_archives = st.checkbox(
        "Enable Historical Analysis (Web Archives)",
        help="Analyze how content changed over time"
    )

    st.divider()

    st.header("ℹ️ About")
    st.info("""
    **Core Capabilities**
    - Static & dynamic scraping
    - AI summarization and Q&A
    - Chat with scraped content
    - Domain-aware scraping
    - Future-ready RAG architecture
    """)

    if st.session_state.scraped_data:
        st.divider()
        st.success("✅ Content loaded")
        if st.button("🗑️ Clear Session"):
            st.session_state.scraped_data = None
            st.session_state.chat_history = []
            if st.session_state.gemini_handler:
                st.session_state.gemini_handler.clear_context()
            st.rerun()

# =========================
# Main Input Section
# =========================
col1, col2 = st.columns([2, 1])

with col1:
    url = st.text_input(
        "🌐 Enter Website URL",
        placeholder="https://example.com"
    )

with col2:
    st.write("")
    st.write("")
    scrape_button = st.button("🚀 Scrape Website", type="primary", use_container_width=True)

# =========================
# Scraping Logic
# =========================
if scrape_button and url:
    if not url.startswith(("http://", "https://")):
        st.error("❌ Please enter a valid URL starting with http:// or https://")
    else:
        with st.spinner("🔄 Scraping website..."):
            parser = WebParser()
            result = parser.scrape(url, use_selenium=use_selenium)

            if result["success"]:
                st.session_state.scraped_data = result

                if api_key:
                    try:
                        st.session_state.gemini_handler = GeminiHandler(api_key)
                        st.session_state.gemini_handler.set_context(
                            result["content"],
                            result["title"],
                            result["description"]
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Gemini initialization failed: {str(e)}")

                st.markdown(
                    f'<div class="success-box">✅ Scraped successfully using {result["method"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="error-box">❌ Error: {result["error"]}</div>',
                    unsafe_allow_html=True
                )

# =========================
# Display Results
# =========================
if st.session_state.scraped_data:
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📄 Content", "🤖 AI Analysis", "💬 Chat"])

    data = st.session_state.scraped_data

    # -------- Tab 1: Content --------
    with tab1:
        st.subheader("Scraped Content")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {data['title']}")
        with col2:
            st.markdown(f"**Method:** {data['method']}")

        st.markdown(f"**Description:** {data['description']}")

        with st.expander("📖 View Full Content"):
            st.text_area(
                "Content",
                value=data["content"],
                height=400,
                label_visibility="collapsed"
            )

        col1, col2, col3 = st.columns(3)
        col1.metric("Characters", len(data["content"]))
        col2.metric("Words", len(data["content"].split()))
        col3.metric("Lines", len(data["content"].splitlines()))

    # -------- Tab 2: AI Analysis --------
    with tab2:
        st.subheader("AI-Powered Analysis")

        if not st.session_state.gemini_handler:
            st.warning("⚠️ Please provide a valid Gemini API key")
        else:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📝 Summarize", use_container_width=True):
                    with st.spinner("Generating summary..."):
                        res = st.session_state.gemini_handler.summarize()
                        if res["success"]:
                            st.write(res["response"])
                        else:
                            st.error(res["error"])

            with col2:
                task = st.selectbox(
                    "Quick Analysis",
                    [
                        "Extract key points",
                        "List main topics",
                        "Identify important facts",
                        "Find action items",
                        "Extract statistics"
                    ]
                )
                if st.button("🔍 Analyze", use_container_width=True):
                    with st.spinner("Analyzing..."):
                        res = st.session_state.gemini_handler.extract_insights(task.lower())
                        if res["success"]:
                            st.write(res["response"])
                        else:
                            st.error(res["error"])

            st.divider()

            custom_task = st.text_area(
                "Custom Analysis",
                placeholder="Ask a specific question about the content..."
            )

            if st.button("🎯 Run Custom Task", use_container_width=True):
                if custom_task:
                    res = st.session_state.gemini_handler.extract_insights(custom_task)
                    if res["success"]:
                        st.write(res["response"])
                    else:
                        st.error(res["error"])

    # -------- Tab 3: Chat --------
    with tab3:
        st.subheader("💬 Chat with Content")

        if not st.session_state.gemini_handler:
            st.warning("⚠️ Please provide a valid Gemini API key")
        else:
            for chat in st.session_state.chat_history:
                with st.chat_message(chat["role"]):
                    st.write(chat["content"])

            question = st.chat_input("Ask something about the content...")
            if question:
                st.session_state.chat_history.append(
                    {"role": "user", "content": question}
                )

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        res = st.session_state.gemini_handler.ask_question(question)
                        if res["success"]:
                            st.write(res["response"])
                            st.session_state.chat_history.append(
                                {"role": "assistant", "content": res["response"]}
                            )
                        else:
                            st.error(res["error"])

else:
    st.markdown("""
    ### 👋 Welcome

    Enter a URL and click **Scrape Website** to begin.

    **You can:**
    - Scrape static & dynamic websites  
    - Generate AI summaries  
    - Ask questions & chat with content  
    - Perform structured analysis  
    """)

# =========================
# Footer
# =========================
st.divider()
st.markdown(
    "<div style='text-align:center;color:#666;font-size:0.9rem;'>"
    "Built with Streamlit, BeautifulSoup, Selenium & Gemini AI"
    "</div>",
    unsafe_allow_html=True
)
