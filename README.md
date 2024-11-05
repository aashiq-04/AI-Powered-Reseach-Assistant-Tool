# PDF Query Application

## Overview
This project is a web application that allows users to upload PDF files, embed the document data into a vector store, and query the embedded documents to receive relevant responses. The project uses **FastAPI** for the backend and **ReactJS** for the frontend. **LangChain** is employed for text embedding and retrieval.

## Features
- 📂 Upload PDF files to the server.
- 🧠 Embed content of uploaded PDFs into a vector store.
- ❓ Query embedded documents using natural language.
- 🔄 CORS-enabled for backend-frontend communication.
- ⚡ Built with modern web technologies: **FastAPI** and **ReactJS**.

## Tech Stack
### Backend
- **FastAPI**: Fast and efficient web framework for Python.
- **LangChain**: Framework for developing language model-powered applications.
- **FAISS**: Library for efficient similarity search and clustering.
- **PyPDF2**: PDF processing library.
- **UnstructuredPDFLoader**: Utility for content extraction from PDFs.

### Frontend
- **ReactJS**: Library for building user interfaces.

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Node.js and npm (for React frontend)
- Required Python packages (see `requirements.txt`)

### Backend Setup
1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/pdf-query-app.git
    cd pdf-query-app
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` file** and add the Groq API key:
    ```env
    GROQ_API_KEY=your_api_key_here
    ```

5. **Run the FastAPI server**:
    ```bash
    uvicorn main:app --reload
    ```

### Frontend Setup
1. **Navigate to the `frontend` directory**:
    ```bash
    cd frontend
    ```

2. **Install dependencies**:
    ```bash
    npm install
    ```

3. **Start the React development server**:
    ```bash
    npm start
    ```

### Running the Application
- **Backend API**: `http://127.0.0.1:8000`
- **Frontend UI**: `http://localhost:3000`

## API Endpoints
### `POST /upload`
- **Description**: Uploads a PDF file and saves it to the `data` directory.
- **Request**: `multipart/form-data`
- **Response**: JSON indicating success or failure.

### `POST /embed`
- **Description**: Processes uploaded PDFs, splits content into chunks, embeds text, and creates a vector store.
- **Response**: JSON with details about the documents processed and time taken.

### `POST /query`
- **Description**: Accepts a question and retrieves the most relevant answer from the embedded documents.
- **Request Body**:
    ```json
    {
      "question": "What is the main topic of the document?"
    }
    ```
- **Response**: JSON with the answer and context.


