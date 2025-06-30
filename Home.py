import streamlit as st
st.set_page_config(
    page_title="Legal AI Chat", 
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚖️"
)

# Initialize sidebar state first
if "sidebar_visible" not in st.session_state:
    st.session_state.sidebar_visible = False

# Hamburger menu button at the top
button_text = "✕ Close" if st.session_state.sidebar_visible else "☰ Menu"
if st.button(button_text, key="hamburger_menu", help="Toggle sidebar navigation"):
    # Toggle sidebar state
    st.session_state.sidebar_visible = not st.session_state.sidebar_visible
    st.rerun()

# Always show sidebar content but control visibility with CSS
st.sidebar.title("Navigation")
st.sidebar.write("🔍 Debug: Sidebar visible = True")

# Add navigation links
st.sidebar.markdown("---")
st.sidebar.markdown("### Pages")
st.sidebar.markdown("- [Home](/)")
st.sidebar.markdown("- [Draft Generator](/draft_generator)")
st.sidebar.markdown("- [Law Reference Search](/Law_Reference_Search)")

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Actions")
if st.sidebar.button("Clear Chat", key="clear_chat"):
    st.session_state.messages = []
    st.rerun()
    
if st.sidebar.button("Reset App", key="reset_app"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

from streamlit_chat import message
from modules.parse_doc import extract_text_from_pdf, extract_text_from_docx
from modules.analyze_doc import analyze_text_with_openai
from modules.legal_search import load_legal_knowledge_base, answer_question_from_lawbase
from langgraph_workflow import create_legal_agent
from dotenv import load_dotenv
import os
from typing import Optional
st.write("🧪 Pages folder contents:", os.listdir("pages"))

# Gradient header banner
st.markdown("""
<div style="
    background: linear-gradient(135deg, #3F51B5 0%, #6366F1 100%);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 30px;
    text-align: center;
">
    <h1 style="
        color: white;
        font-family: 'Segoe UI', sans-serif;
        font-weight: bold;
        margin: 0;
        font-size: 28px;
    ">🤖 Steve, your AI Legal Assistant</h1>
</div>
""", unsafe_allow_html=True)

# Modern SaaS Dark Mode Styling
st.markdown("""
<style>
/* Global font and app styling */
.stApp {
    font-family: 'Segoe UI', sans-serif;
    background-color: #181824 !important;
}

html, body, #root, .block-container {
    background-color: #181824 !important;
    color: #e2e2e2;
    font-family: 'Segoe UI', sans-serif;
}

/* File uploader dark mode styling */
.stFileUploader {
    background-color: #1f1f2e !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 20px !important;
    margin: 20px 0 !important;
}

.stFileUploader > div {
    background-color: #1f1f2e !important;
    border: none !important;
}

.stFileUploader > div > div {
    background-color: #1f1f2e !important;
    border: none !important;
}

.stFileUploader > div > div > div {
    background-color: #1f1f2e !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 15px !important;
    box-shadow: none !important;
}

/* File uploader text styling */
.stFileUploader label {
    color: #ccc !important;
    font-family: 'Segoe UI', sans-serif !important;
}

.stFileUploader > div > div > div > div {
    color: #ccc !important;
}

.stFileUploader small {
    color: #999 !important;
}

/* Browse files button styling */
.stFileUploader button {
    background-color: #2a2b38 !important;
    color: #ccc !important;
    border: 1px solid #555 !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    font-family: 'Segoe UI', sans-serif !important;
}

.stFileUploader button:hover {
    background-color: #34353f !important;
    border-color: #666 !important;
    box-shadow: none !important;
}

.stFileUploader button:focus {
    box-shadow: none !important;
    border-color: #3F51B5 !important;
}

/* Remove any white backgrounds or glows */
.stFileUploader * {
    box-shadow: none !important;
}

.stFileUploader:hover {
    border-color: #666 !important;
    box-shadow: none !important;
}

.stFileUploader:focus-within {
    border-color: #3F51B5 !important;
    box-shadow: none !important;
}

/* Drag and drop area styling */
.stFileUploader > div > div > div[data-testid="stFileUploaderDropzone"] {
    background-color: #1f1f2e !important;
    border: 2px dashed #444 !important;
    border-radius: 10px !important;
    color: #ccc !important;
}

.stFileUploader > div > div > div[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #666 !important;
    background-color: #252536 !important;
}

/* Chat input styling */
.stChatInputContainer > div {
    background-color: #1e1f26 !important;
    border: 1px solid #3F51B5 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}

.stChatInput > div > div > textarea {
    background-color: #1e1f26 !important;
    color: white !important;
    border: none !important;
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 15px !important;
}

.stChatInput > div > div > textarea::placeholder {
    color: white !important;
    opacity: 0.7;
}

/* Conversation container smooth scrolling */
.main .block-container {
    scroll-behavior: smooth;
}

/* Streamlit chat message styling */
.stChatMessage {
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 15px !important;
    max-width: 80% !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin: 8px 0 !important;
    box-shadow: none !important;
}

/* Assistant messages */
.stChatMessage[data-testid="chat-message-assistant"] {
    background-color: #2a2b38 !important;
    color: #e2e2e2 !important;
}

/* User messages */  
.stChatMessage[data-testid="chat-message-user"] {
    background-color: #3f51b5 !important;
    color: white !important;
    font-weight: bold !important;
}

/* Alternative styling for streamlit_chat messages */
div[data-testid="user"] {
    background-color: #3f51b5 !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    max-width: 80% !important;
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 15px !important;
    box-shadow: none !important;
}

div[data-testid="assistant"] {
    background-color: #2a2b38 !important;
    color: #e2e2e2 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    max-width: 80% !important;
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 15px !important;
    box-shadow: none !important;
}

/* Remove Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hamburger menu button */
.hamburger-container {
    position: fixed;
    top: 10px;
    left: 10px;
    z-index: 1000;
}

.hamburger-btn {
    background: #3F51B5;
    border: none;
    border-radius: 5px;
    padding: 8px 12px;
    cursor: pointer;
    color: white;
    font-size: 18px;
    font-weight: bold;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    transition: background 0.3s;
}

.hamburger-btn:hover {
    background: #5C6BC0;
}

/* Make sure the button is visible */
.stButton > button {
    background: #3F51B5 !important;
    color: white !important;
    border: none !important;
    border-radius: 5px !important;
    padding: 8px 12px !important;
    font-size: 18px !important;
    font-weight: bold !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}

.stButton > button:hover {
    background: #5C6BC0 !important;
}

/* Sidebar toggle functionality */
.sidebar-hidden {
    display: none !important;
}

/* Add margin to main content when sidebar is shown */
.main-content {
    margin-left: 0;
    transition: margin-left 0.3s;
}

.main-content.sidebar-visible {
    margin-left: 250px;
}
</style>
""", unsafe_allow_html=True)

# JavaScript to hide/show sidebar
sidebar_visibility = "block" if st.session_state.sidebar_visible else "none"
st.markdown(f"""
<script>
function toggleSidebar() {{
    const sidebar = document.querySelector('.css-1d391kg');
    if (sidebar) {{
        sidebar.style.display = '{sidebar_visibility}';
    }}
}}
toggleSidebar();
</script>
""", unsafe_allow_html=True)

# 🔐 Load API Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ OPENAI_API_KEY is not set. Please set it in your .env file.")
    st.stop()

# 🧠 Initialize LangGraph Legal Agent
legal_agent = create_legal_agent(OPENAI_API_KEY)



# 🧠 Session state init
if "messages" not in st.session_state:
    st.session_state.messages = []
if "legal_text" not in st.session_state:
    st.session_state.legal_text = ""
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# 📄 File Upload Section
uploaded_file = st.file_uploader(
    "📄 Upload a legal document (PDF or DOCX)",
    type=["pdf", "docx"],
    help="Drag and drop your document here or click to browse"
)

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        st.session_state.legal_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        st.session_state.legal_text = extract_text_from_docx(uploaded_file)

    with st.spinner("Analyzing document..."):
        summary = analyze_text_with_openai(st.session_state.legal_text, OPENAI_API_KEY)
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"**📄 Summary of uploaded document:**\n\n{summary}"
        })

    with st.spinner("Indexing legal reference base..."):
        st.session_state.vectorstore = load_legal_knowledge_base(OPENAI_API_KEY)

    st.success("✅ Document processed and ready for Q&A!")

# 💬 Chat Input
user_input = st.chat_input("Type your message...", key="main_input")

# Add spacer
st.markdown("<br><br>", unsafe_allow_html=True)

# 🧠 Process user input with LangGraph Agent
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        try:
            # Debug: Log uploaded document text snippet
            st.write(f"🔍 Debug - Legal text preview: {st.session_state.legal_text[:200]}...")
            
            result = legal_agent.invoke({
                "input": user_input,
                "legal_text": st.session_state.legal_text,
                "vectorstore": st.session_state.vectorstore
            })
            
            # Debug: Show full result dictionary
            DEV_MODE = True

            if DEV_MODE:
               st.expander("🔍 Debug - LangGraph Output").code(result, language="json")

            
            # Add fallback for missing or empty output
            output = result.get("output", "⚠️ No response generated.")
            if not output or output.strip() == "":
                output = "⚠️ No response generated."
            
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {e}"})

# 🪄 Display chat history
st.markdown("#### 💬 Conversation History")

for idx, msg in enumerate(st.session_state.messages):
    message(
        msg["content"],
        is_user=(msg["role"] == "user"),
        key=f"{msg['role']}_{idx}",
        allow_html=True
    )
