# main.py
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import pickle
import time
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2  # Ensure you have this installed
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Groq API KEY
groq_api_key = os.environ['GROQ_API_KEY']
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Initialize embeddings
embedding = HuggingFaceEmbeddings()
vector_store = None  # Initialize vector store

class Question(BaseModel):
    question: str

VECTOR_STORE_PATH = "vector_store.pkl"

@app.get("/")
async def root():
    return {
        "message": "Welcome to the PDF Query API",
        "endpoints": {
            "/embed": "POST - Embed documents from uploaded PDF",
            "/query": "POST - Query the embedded documents"
        }
    }

@app.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    if pdf is None:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    try:
        # Ensure the data directory exists
        os.makedirs('./data', exist_ok=True)

        # Save the uploaded PDF to the data directory
        file_location = f"./data/{pdf.filename}"
        with open(file_location, "wb") as file:
            file.write(await pdf.read())

        return JSONResponse(content={"message": "PDF uploaded successfully."})
    except Exception as e:
        print(f"Error occurred while uploading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/embed")
async def embed_documents():
    global vector_store
    try:
        # Use PyPDFLoader to load PDFs from the data directory
        loader = DirectoryLoader(
            "./data",
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        
        docs = loader.load()
        
        if not docs:
            raise HTTPException(status_code=400, detail="No documents found in ./data directory")

        # Continue with the embedding process...
        # (rest of your embedding logic)
        
        return {
            "message": "Embedding process completed successfully.",
            # Include any additional information you want to return
        }
    except Exception as e:
        print(f"Error occurred during embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/query", description="Query the embedded documents with a question")
async def query_documents(question: Question):
    global vector_store
    if vector_store is None:
        raise HTTPException(status_code=400, detail="Vector store not created. Please call /embed first.")
    
    if not question.question:
        raise HTTPException(status_code=400, detail="Question is required.")

    try:
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

        # Ensure the response contains the expected keys
        answer = response.get('answer', 'No answer found.')
        context = response.get('context', 'No context available.')

        return {"answer": answer, "context": context}
    except Exception as e:
        print(f"Error occurred during query processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def extract_text_from_pdf(contents):
    # Use PyPDF2 to extract text from th PDF
    reader = PyPDF2.PdfReader(contents)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
