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
import shutil

load_dotenv()

# Define the temporary directory path
TEMP_DIR = "./data"

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

# Function to create the temporary directory
def create_temp_directory():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

# Function to clear the temporary directory
def clear_temp_directory():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)  # Remove the directory and its contents
        os.makedirs(TEMP_DIR)     # Recreate the directory

@app.on_event("startup")
async def startup_event():
    create_temp_directory()  # Create the temp directory on startup
    clear_temp_directory()    # Clear any existing files

@app.on_event("shutdown")
async def shutdown_event():
    clear_temp_directory()  # Clear the temp directory on shutdown

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
        return JSONResponse(content={"message": "No file uploaded."}, status_code=400)

    try:
        # Save the uploaded PDF to the temporary directory
        file_location = os.path.join(TEMP_DIR, pdf.filename)
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
        # Initialize the embeddings and document loader
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        loader = DirectoryLoader(
            TEMP_DIR,  # Use the 'data' directory for embedding
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        
        # Load documents from the temporary directory
        docs = loader.load()
        
        if not docs:
            raise HTTPException(status_code=400, detail="No documents found in the temporary directory. Please check the upload.")

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.split_documents(docs)
        
        if not final_documents:
            raise HTTPException(status_code=400, detail="No text could be extracted from the documents. Please check the content of the PDF files.")

        # Create the vector store from the final documents
        vector_store = FAISS.from_documents(final_documents, embedding)

        # Save the vector store to a file
        with open(VECTOR_STORE_PATH, 'wb') as f:
            pickle.dump(vector_store, f)

        return {
            "message": "Embedding process completed successfully.",
        }
    except Exception as e:
        print(f"Error occurred during embedding: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Load the vector store at startup
def load_vector_store():
    global vector_store
    if os.path.exists(VECTOR_STORE_PATH):
        with open(VECTOR_STORE_PATH, 'rb') as f:
            vector_store = pickle.load(f)
    else:
        vector_store = None  # Initialize as None if the file does not exist

@app.post("/query", description="Query the embedded documents with a question")
async def query_documents(question: Question):
    global vector_store
    if vector_store is None:
        raise HTTPException(status_code=400, detail="Vector store not created. Please call /embed url first.")
    
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
    print("Starting the server and deleting uploaded PDFs...")
    load_vector_store()  # Load the vector store when the app starts
    print("App is starting")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
