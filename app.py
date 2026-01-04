import streamlit as st
from backend.parser import WebParser
from backend.gemini_handler import GeminiHandler
import time
import os


# Page configuration
st.set_page_config(
    page_title="AI Web Scraper & Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
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


# Initialize session state
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None
if 'gemini_handler' not in st.session_state:
    st.session_state.gemini_handler = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.markdown('<div class="main-header">🔍 AI Web Scraper & Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Scrape any website and chat with the content using Gemini AI</div>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        placeholder="Enter your Gemini API key",
        type="password"
    )

    st.divider()
    
    st.header("📋 Options")
    use_selenium = st.checkbox(
        "Use Selenium (for dynamic sites)",
        value=False,
        help="Enable for JavaScript-heavy websites"
    )
    
    st.divider()
    
    st.header("ℹ️ About")
    st.info("""
    **Features:**
    - Scrape any website
    - Auto-summarization
    - Ask questions about content
    - Extract insights
    - Support for dynamic sites
    """)
    
    if st.session_state.scraped_data:
        st.divider()
        st.success("✅ Content loaded!")
        if st.button("🗑️ Clear Content"):
            st.session_state.scraped_data = None
            st.session_state.chat_history = []
            if st.session_state.gemini_handler:
                st.session_state.gemini_handler.clear_context()
            st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # URL input
    url = st.text_input(
        "🌐 Enter Website URL",
        placeholder="https://example.com",
        help="Enter the URL of the website you want to scrape"
    )

with col2:
    st.write("")
    st.write("")
    scrape_button = st.button("🚀 Scrape Website", type="primary", use_container_width=True)

# Scraping logic
if scrape_button and url:
    if not url.startswith(('http://', 'https://')):
        st.error("❌ Please enter a valid URL starting with http:// or https://")
    else:
        with st.spinner("🔄 Scraping website..."):
            parser = WebParser()
            result = parser.scrape(url, use_selenium=use_selenium)
            
            if result['success']:
                st.session_state.scraped_data = result
                
                # Initialize Gemini handler
                if api_key:
                    try:
                        st.session_state.gemini_handler = GeminiHandler(api_key)
                        st.session_state.gemini_handler.set_context(
                            result['content'],
                            result['title'],
                            result['description']
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Could not initialize Gemini: {str(e)}")
                
                st.markdown(f'<div class="success-box">✅ Successfully scraped using {result["method"]}!</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">❌ Error: {result["error"]}</div>', unsafe_allow_html=True)

# Display scraped content
if st.session_state.scraped_data:
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📄 Content", "🤖 AI Analysis", "💬 Chat"])
    
    with tab1:
        st.subheader("Scraped Content")
        
        data = st.session_state.scraped_data
        
        # Metadata
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {data['title']}")
        with col2:
            st.markdown(f"**Method:** {data['method']}")
        
        st.markdown(f"**Description:** {data['description']}")
        
        st.divider()
        
        # Content
        with st.expander("📖 View Full Content", expanded=False):
            st.text_area(
                "Content",
                value=data['content'],
                height=400,
                label_visibility="collapsed"
            )
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Characters", f"{len(data['content']):,}")
        with col2:
            st.metric("Words", f"{len(data['content'].split()):,}")
        with col3:
            st.metric("Lines", f"{len(data['content'].splitlines()):,}")
    
    with tab2:
        st.subheader("AI-Powered Analysis")
        
        if not st.session_state.gemini_handler:
            st.warning("⚠️ Please enter a valid Gemini API key in the sidebar")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📝 Summarize", use_container_width=True):
                    with st.spinner("Generating summary..."):
                        result = st.session_state.gemini_handler.summarize()
                        if result['success']:
                            st.markdown("### Summary")
                            st.write(result['response'])
                        else:
                            st.error(f"Error: {result['error']}")
            
            with col2:
                task_options = [
                    "Extract key points",
                    "List main topics",
                    "Identify important facts",
                    "Find action items",
                    "Extract statistics"
                ]
                selected_task = st.selectbox("Quick Analysis", task_options)
                
                if st.button("🔍 Analyze", use_container_width=True):
                    with st.spinner(f"Performing: {selected_task}..."):
                        result = st.session_state.gemini_handler.extract_insights(selected_task.lower())
                        if result['success']:
                            st.markdown(f"### {selected_task}")
                            st.write(result['response'])
                        else:
                            st.error(f"Error: {result['error']}")
            
            st.divider()
            
            # Custom task
            st.markdown("### Custom Analysis")
            custom_task = st.text_area(
                "What would you like to know?",
                placeholder="E.g., 'What are the main arguments in this article?' or 'Extract all dates mentioned'",
                height=100
            )
            
            if st.button("🎯 Execute Custom Task", use_container_width=True):
                if custom_task:
                    with st.spinner("Processing..."):
                        result = st.session_state.gemini_handler.extract_insights(custom_task)
                        if result['success']:
                            st.markdown("### Result")
                            st.write(result['response'])
                        else:
                            st.error(f"Error: {result['error']}")
                else:
                    st.warning("Please enter a task")
    
    with tab3:
        st.subheader("💬 Chat with Content")
        
        if not st.session_state.gemini_handler:
            st.warning("⚠️ Please enter a valid Gemini API key in the sidebar")
        else:
            # Display chat history
            for i, chat in enumerate(st.session_state.chat_history):
                with st.chat_message(chat['role']):
                    st.write(chat['content'])
            
            # Chat input
            question = st.chat_input("Ask a question about the content...")
            
            if question:
                # Add user message
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': question
                })
                
                with st.chat_message("user"):
                    st.write(question)
                
                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        result = st.session_state.gemini_handler.ask_question(question)
                        
                        if result['success']:
                            response = result['response']
                            st.write(response)
                            
                            # Add assistant message
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': response
                            })
                        else:
                            error_msg = f"Error: {result['error']}"
                            st.error(error_msg)
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': error_msg
                            })

else:
    # Welcome message
    st.markdown("""
    ### 👋 Welcome!
    
    Get started by entering a URL above and clicking "Scrape Website".
    
    **What you can do:**
    1. **Scrape** any website (static or dynamic)
    2. **Summarize** the content automatically
    3. **Ask questions** about the scraped data
    4. **Extract insights** like key points, statistics, and more
    5. **Chat** with the content using Gemini AI
    
    **Tips:**
    - Enable "Use Selenium" for JavaScript-heavy websites
    - Try different analysis tasks to explore the content
    - Use the chat feature for detailed Q&A
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Built with Streamlit, BeautifulSoup, Selenium & Gemini AI
</div>
""", unsafe_allow_html=True)