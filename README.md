PDF Query Application
Overview
This project is a web application that allows users to upload PDF files, embed the document data into a vector store, and query the embedded documents to receive relevant responses. The project leverages FastAPI for the backend and ReactJS for the frontend. LangChain is used for text embedding and retrieval, and FAISS is utilized as the vector store.

Features
Upload PDF files to a server.
Process and embed the content of uploaded PDFs into a vector store.
Query the embedded documents using natural language and receive contextually relevant answers.
Built with FastAPI for the backend and ReactJS for the frontend interface.
CORS enabled to support communication between the backend and frontend.
Tech Stack
Backend
FastAPI: Used for building the API server.
LangChain: Used for document processing and text embedding.
FAISS: Vector store for storing and retrieving document embeddings.
PyPDF2: For reading PDF files.
UnstructuredPDFLoader: To extract content from PDFs.
Frontend
ReactJS: Used for building a dynamic user interface.
Installation and Setup
Prerequisites
Python 3.8 or higher
Node.js and npm (for React frontend)
Required Python packages listed in requirements.txt
