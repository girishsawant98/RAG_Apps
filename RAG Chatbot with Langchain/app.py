### Creating a RAG Chatbot with Langchain and Streamlit

import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
import streamlit as st
from src.rag_chain import create_rag_chain
from src.doc_preprocessor import process_document

#Load environment variables
load_dotenv()

st.set_page_config(page_title="RAG Chatbot 🤖", page_icon="📚")
st.title("📚 RAG Chatbot: Document Q&A")

#Initialize session state
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

#File uploader
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "gif"])

if uploaded_file is not None:
    if st.button("Process file"):
        with st.spinner("Processing document..."):
            #Save uploaded file to a temporary location
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                #Process document and create RAG chain
                chunks = process_document(uploaded_file.name)
                st.session_state.rag_chain = create_rag_chain(chunks)
                st.success("Document processed successfully! You can now ask questions.")

            except ValueError as e:
                st.error(f"Error: {e}")
            finally:
                #Clean up temporary file
                os.remove(uploaded_file.name)
 
 #Query input
query = st.text_input("Ask a question about the uploaded document")

if st.button("Ask"):
    if st.session_state.rag_chain and query:
        with st.spinner("Generating answer..."):
            answer = st.session_state.rag_chain.invoke({"question": query})
            st.subheader("Answer:")
            st.write(answer)
    elif not st.session_state.rag_chain:
        st.error("Please upload and process a document first.")    
    else:
        st.error("Please enter a question to ask.")                                                                          



        
