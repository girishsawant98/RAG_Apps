import os 
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers  import StrOutputParser
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough
load_dotenv()

#Load the API keys from .env file
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"   
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")


RAG_PROMPT_TEMPLATE = """
You are a helpful coding assistant that can answer questions about the provided context.The context is usually a PDF document or an image (screenshot) of a code file. Augment your answers with code snippets from the context if necessary.

If you don't know the answer, say you don't know.

Context: {context}
Question: {question}
"""

rag_prompt=ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

#RAG Chain function
def create_rag_chain(chunks):
    #Embedding
    embedding_model=OllamaEmbeddings(model="all-minilm:latest")
    doc_search =FAISS.from_documents(chunks, embedding_model)
    retriever=doc_search.as_retriever(search_type="similarity", search_kwargs={"k":5})

    #Ollama Gemma3 model
    llm=Ollama(model="llama3.2:3b", temperature=0)
    output_parser=StrOutputParser()

    #RAG Chain
    rag_chain=(
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | output_parser
    )

    return rag_chain