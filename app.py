import streamlit as st
import os


from backend import embed_and_index_pdf, execute_rag_qa


# 1. Page Configuration and Styling
st.set_page_config(
    page_title="ScholarGPT Workspace", 
    page_icon="📚", 
    layout="centered"
)

st.title("📚 ScholarGPT")
st.subheader("Your Personal Research Assistant")
st.markdown("---")

# 2. Document Handling Section
uploaded_file = st.file_uploader(
    label="Drag and drop your research paper here (PDF)", 
    type=["pdf"]
)


# Check if a file has actually been dropped into the widget
if uploaded_file:
    # Check if this is a brand new file, or if we have already indexed it
    if "retriever" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
        
        with st.spinner("Processing document layout and indexing semantic vector space..."):
            # Streamlit uploads files as in-memory bytes streams. 
            # PyPDFLoader requires a physical file path string, so we create a fast temp file.
            temp_file_name = f"temp_{uploaded_file.name}"
            with open(temp_file_name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Run the backend data pipeline to get our VectorStoreRetriever object
                compiled_retriever = embed_and_index_pdf(temp_file_name)
            
                # Cache the retriever and file name inside the state memory dictionary
                st.session_state["retriever"] = compiled_retriever
                st.session_state["current_file"] = uploaded_file.name
                
                st.success(f"Successfully processed: {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"Critical data ingestion failure: {e}")
                
            finally:
                # Clean up and delete the temporary physical file from the server disk
                if os.path.exists(temp_file_name):
                    os.remove(temp_file_name)

# 3. Interactive Q&A Interface Section
# We only display the text entry box if a document has been successfully processed first
if "retriever" in st.session_state:
    st.markdown("### How can I help you with this research paper?")
    
    # --- FIX: We wrap the input and button inside a form barrier ---
    with st.form(key="qa_form_barrier", clear_on_submit=False):
        user_query = st.text_input(
            label="Enter your prompt:", 
            placeholder="e.g., Explain the core methodology used in section 3.",
        )
        # st.form_submit_button replaces the regular st.button
        submit_button = st.form_submit_button(label="Ask")
    
    # Execution logic now links strictly to the form submit event
    if submit_button and user_query:
        with st.spinner("Searching document context and generating synthesized output..."):
            try:
                ai_response = execute_rag_qa(
                    retriever=st.session_state["retriever"], 
                    user_question=user_query
                )
                
                st.subheader("Analysis Result")
                st.markdown(ai_response)
                
            except Exception as e:
                st.error(f"Inference execution failure: {e}")

