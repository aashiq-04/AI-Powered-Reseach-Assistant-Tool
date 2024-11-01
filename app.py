# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import pickle
import time
from builtins import open

load_dotenv()

app = FastAPI()

# Load Groq API KEY
groq_api_key = os.environ['GROQ_API_KEY']
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Add near the top with other global variables
embedding = HuggingFaceEmbeddings()

class Question(BaseModel):
    question: str

vector_store = None

# Add a path for saved vector store
VECTOR_STORE_PATH = "vector_store.pkl"

@app.get("/")
async def root():
    return {
        "message": "Welcome to the PDF Query API",
        "endpoints": {
            "/embed": "POST - Embed documents from the data directory",
            "/query": "POST - Query the embedded documents",
        }
    }

@app.post("/embed")
async def embed_documents():
    global vector_store
    try:
        start_time = time.time()
        
        print("Starting embedding process...")
        
        # Simplified loader without OCR settings
        loader = DirectoryLoader(
            "./data",
            glob="**/*.pdf",
            loader_cls=UnstructuredPDFLoader
        )
        
        docs = loader.load()
        
        print(f"Found {len(docs)} documents.")
        
        # Debug: Print content of first few documents
        for i, doc in enumerate(docs[:2]):  # Print first 2 docs
            print(f"\nDocument {i+1} content preview:")
            print(f"Content length: {len(doc.page_content)}")
            print(f"Content preview: {doc.page_content[:200]}...")  # First 200 chars
            
        if not docs:
            raise HTTPException(status_code=400, detail="No documents found in ./data directory")

        # Modified text splitting with more lenient parameters
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            is_separator_regex=False
        )
        
        print("\nSplitting documents into chunks...")
        final_documents = text_splitter.split_documents(docs)
        
        # Debug: Print chunks information
        print(f"Created {len(final_documents)} chunks")
        
        if final_documents:
            print(f"First chunk preview: {final_documents[0].page_content[:100]}...")
        
        if not final_documents:
            raise HTTPException(status_code=400, detail="No text could be extracted from documents")

        print(f"Creating vector store with {len(final_documents)} text chunks...")
        vector_store = FAISS.from_documents(final_documents, embedding)
        
        print("Saving vector store to disk...")
        with open(VECTOR_STORE_PATH, "wb") as f:
            pickle.dump(vector_store, f)

        end_time = time.time()
        print("Process completed successfully!")
        return {
            "message": "Vector store created successfully.",
            "time_taken": f"{end_time - start_time:.2f} seconds",
            "documents_processed": len(docs),
            "text_chunks": len(final_documents)
        }
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/query", description="Query the embedded documents with a question")
async def query_documents(question: Question):
    global vector_store
    if vector_store is None:
        raise HTTPException(status_code=400, detail="Vector store not created. Please call /embed first.")
    
    document_chain = create_stuff_documents_chain(llm, ChatPromptTemplate.from_template("""
        Answer the question based on the provided context only.
        Please provide the most accurate response based on the question.

        Context:
        {context}

        Question: {input}

        Answer:
    """))
    
    retriever = vector_store.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke({'input': question.question})
    return {"answer": response['answer'], "context": response["context"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
