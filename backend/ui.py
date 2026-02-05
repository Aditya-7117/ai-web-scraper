def section_title(text):
    return f"""
    <div style="
        font-size:1.4rem;
        font-weight:700;
        margin:1.2rem 0 0.6rem 0;
        color:#e5e7eb;">
        {text}
    </div>
    """

def badge(text):
    return f"""
    <span style="
        background:linear-gradient(90deg,#3b82f6,#0ea5e9);
        color:white;
        padding:0.2rem 0.6rem;
        border-radius:999px;
        font-size:0.75rem;
        margin-left:0.4rem;">
        {text}
    </span>
    """
