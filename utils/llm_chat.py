# utils/llm_chat.py
import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load Word (.docx) file and prepare retriever

_loader = UnstructuredWordDocumentLoader("data/District Incentives Plan.docx")
docs = _loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever()

# Set up Groq LLM using secrets.toml
llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    groq_api_key=st.secrets["GROQ_API_KEY"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False
)

def get_chat_response(question: str) -> str:
    try:
        return qa_chain.run(question)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

