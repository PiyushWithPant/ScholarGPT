import os
from dotenv import load_dotenv

import pprint
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Component 1 & 2: Loading and Slicing
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Component 3: Vector Math and Storage
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

# Component 4: Execution Architecture
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# Safely load local environmental variables (.env)
load_dotenv()




def embed_and_index_pdf(pdf_file_path: str):


    # 1. Load the PDF
    loader = PyPDFLoader(pdf_file_path)
    raw_pages = loader.load()


    # pprint.pprint(raw_pages[0], indent=4)   # Debug: Check the loaded pages

    # 2. Chunk the text - RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    text_chunks = text_splitter.split_documents(raw_pages)

    # pprint.pprint(len(text_chunks))  # Debug: Check the number of text chunks created
    # pprint.pprint(text_chunks[2].page_content, indent=4)  # Debug: Check the first split text chunk

    # 3. Create embeddings and store in Chroma

    # Initialize the Google Generative AI Embeddings
    google_emeddings = GoogleGenerativeAIEmbeddings(model = "gemini-embedding-001")

    # Create a Chroma vector store and add the text chunks
    vector_db = Chroma.from_documents(      # Transient in-memory vector store for testing
        documents = text_chunks,
        embedding = google_emeddings,
        collection_name = "ScholarGPT_pdf_chunks"

    )

    retriever = vector_db.as_retriever(search_kwargs={"k": 1})  # Retrieve top k relevant chunks
    return retriever


def execute_rag_qa(retriever, user_question: str) -> str:

    matching_chunks = retriever.invoke(user_question)

    compiled_context = "\n\n---\n\n".join([doc.page_content for doc in matching_chunks])

    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system", (
                "You are an elite academic research assistant analyzing a single scientific document. "
                "Your task is to answer the user's question using ONLY the factual context blocks provided below.\n\n"
                "CRITICAL OPERATIONAL RULES:\n"
                "1. Rely strictly on direct assertions explicitly stated in the context blocks.\n"
                "2. If the answer is not present or cannot be completely proven by the blocks, respond exactly with: "
                "'I cannot find the answer to that question within the provided research paper.'\n"
                "3. Do not extrapolate, infer, or bring in outside scientific consensus or facts. Also, keep final response limited to under 200 words.\n\n"
                "RESEARCH PAPER CONTEXT BLOCKS:\n{context}"
            )
        ),
        (
            "human", 
            "{question}"
        )
    ])


    # llm = ChatGoogleGenerativeAI(
    #     model = "gemini-2.0-flash",
    #     temperature = 0.0,  # Deterministic output
    # )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.0,  # Deterministic output
    )


    rag_chain = prompt_template | llm | StrOutputParser()  # LCEL Chain: Prompt -> LLM -> String Output

    return rag_chain.invoke(
        {
            "context": compiled_context,
            "question": user_question
        }
    )













#! TESTING

# if __name__ == "__main__":

#     # 1. Testing PDF loading and text splitting

#     pdf_path = "data/pdf/rag_notes.pdf"  # Ensure this file exists in your directory
#     embed_and_index_pdf(pdf_path)

