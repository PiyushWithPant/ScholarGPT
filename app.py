import streamlit as st
import os

from backend import embed_and_index_pdf, execute_rag_qa

# 1. Page Configuration and Styling
st.set_page_config(
    page_title="ScholarGPT Workspace", 
    page_icon="📚", 
    layout="centered"
)

# Injecting Custom CSS for a highly attractive typography, gradients, and layout fixes
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500&display=swap');

        /* Main background gradient */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
            color: #f8fafc;
        }
        
        /* Premium Gradient Header Styling with an infinite 2s glowing animation loop */
        .gradient-title {
            background: linear-gradient(90deg, #38bdf8 0%, #ec4899 35%, #a855f7 70%, #38bdf8 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 5rem !important;
            font-weight: 900;
            text-align: center;
            margin-bottom: 0px;
            padding-bottom: 0px;
            letter-spacing: -2px;
            font-family: 'Cabinet Grotesk', 'Poppins', 'Inter', sans-serif;
            animation: glow 2s linear infinite;
        }

        @keyframes glow {
            0% { background-position: 0% center; }
            100% { background-position: 200% center; }
        }

        .gradient-subtitle {
            color: #94a3b8 !important;
            text-align: center;
            font-size: 1.5rem !important;
            font-weight: 400;
            margin-top: 8px;
            margin-bottom: 50px;

        }
        
        /* Make crisp text fonts */
        p, label, .stMarkdown {
            color: #f1f5f9 !important;
            font-family: 'Inter', sans-serif;
        }

        /* HIDE THE DEFAULT STREAMLIT 200MB FILE SIZE WARNING */
        [data-testid="stFileUploaderLimitHint"] {
            display: none !important;
        }

        /* Style the file uploader dropzone */
        .stFileUploader section {
            background-color: rgba(30, 41, 59, 0.5) !important;
            border: 2px dashed rgba(168, 85, 247, 0.6) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            transition: border-color 0.3s ease;
        }
        .stFileUploader section:hover {
            border-color: #ec4899 !important;
        }

        /* Style the Q&A form card block */
        [data-testid="stForm"] {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(168, 85, 247, 0.4) !important;
            border-radius: 16px !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3) !important;
            padding: 2rem !important;
        }

        /* Beautify the input text field */
        .stTextInput input {
            background-color: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
        }
        .stTextInput input:focus {
            border-color: #a855f7 !important;
            box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.5) !important;
        }

        /* Gradient Submit Button Styling */
        .stButton button, button[kind="formSubmit"] {
            background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 2rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        .stButton button:hover, button[kind="formSubmit"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4) !important;
        }
        
        /* User Chat Bubble Styling */
        .user-box {
            background-color: rgba(56, 189, 248, 0.1);
            border-left: 4px solid #38bdf8;
            padding: 1rem 1.5rem;
            border-radius: 4px 12px 12px 4px;
            margin-top: 1rem;
            font-weight: 600;
        }

        /* Polished Response Box Container */
        .response-box {
            background-color: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #ec4899;
            padding: 1.5rem;
            border-radius: 4px 12px 12px 4px;
            margin-top: 0.5rem;
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Modernized Title Components
st.markdown('<h1 class="gradient-title">ScholarGPT</h1>', unsafe_allow_html=True)
st.markdown('<p class="gradient-subtitle">Your Personal AI Research Assistant and Study Buddy!</p>', unsafe_allow_html=True)

# Initialize structural limit and chat list arrays within global session dictionary
if "query_count" not in st.session_state:
    st.session_state["query_count"] = 0
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 2. Document Handling Section
uploaded_file = st.file_uploader(
    label="Drop in any document and let me analyze it for you!", 
    type=["pdf"],
    accept_multiple_files=False,

)

# Static slot allocated for processing loader feedbacks cleanly
status_container = st.empty()

# Check if a file has actually been dropped into the widget
if uploaded_file:
    if "retriever" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
        
        with status_container.container():
            with st.spinner("I am braining over it now..."):
                temp_file_name = f"temp_{uploaded_file.name}"
                with open(temp_file_name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    compiled_retriever = embed_and_index_pdf(temp_file_name)
                
                    st.session_state["retriever"] = compiled_retriever
                    st.session_state["current_file"] = uploaded_file.name
                    st.session_state["query_count"] = 0  # Reset inquiry counter for new paper uploads
                    st.session_state["chat_history"] = []  # Clear previous chat list frames
                    
                    st.success(f"Read it all! thanks for uploading {uploaded_file.name}")
                    
                except Exception as e:
                    st.error(f"Sorry, my brain is not braining right now :-(")
                    st.error(f"{e}")
                    
                finally:
                    if os.path.exists(temp_file_name):
                        os.remove(temp_file_name)

# 3. Interactive Q&A Interface Section
if "retriever" in st.session_state:
    st.markdown("### So where should we dive in first?")
    
    # Check if user has depleted their explicit allowance of 3 prompts
    if st.session_state["query_count"] >= 3:
        st.warning("You have reached the session limit of 3 questions for this document.")
    else:
        # Secure Form Input Guardrail with native text field automated value resetting
        # clear_on_submit=True clears out the question text field immediately upon clicking 'Ask'
        with st.form(key="qa_form_barrier", clear_on_submit=True):
            user_query = st.text_input(
                label="Ask me anything about the document!",
                # label=f"Enter your prompt (Questions remaining: {3 - st.session_state['query_count']}):", 
                placeholder="e.g., Explain the core concept, or list the main takeaways...",
            )
            submit_button = st.form_submit_button(label="Ask me!")
        
        if submit_button and user_query:
            # Enforce maximum safe character boundary length for the prompt string
            if len(user_query) > 250:
                st.error("Question length too long. Please restrict your query to under 250 characters.")
            else:
                # Increment state metric securely upon verified input
                st.session_state["query_count"] += 1
                
                with status_container.container():
                    with st.spinner("Ummm let me think..."):
                        try:
                            ai_response = execute_rag_qa(
                                retriever=st.session_state["retriever"], 
                                user_question=user_query
                            )
                            
                            # Append structural tuples straight into the session matrix loop stack
                            st.session_state["chat_history"].append((user_query, ai_response))
                            
                            # Force an instant app redraw to cleanly display changes and refresh remaining quotas
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Inference execution failure: {e}")

    # 4. Chat History Log Display Frame (Positioned at the very bottom to build downstream feeds)
    if st.session_state["chat_history"]:
        for question, answer in st.session_state["chat_history"]:
            st.markdown(f'<div class="user-box">❓ Question: {question}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="response-box">{answer}</div>', unsafe_allow_html=True)