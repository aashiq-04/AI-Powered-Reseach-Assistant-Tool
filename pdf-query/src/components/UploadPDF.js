import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';

const UploadPDF = () => {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (file) => {
    setIsLoading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('pdf', file);

    try {
      const response = await fetch('http://localhost:8000/embed', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setMessage(data.message || 'File uploaded and processed successfully!');

      if (response.ok) {
        navigate('/query');
      }
    } catch (error) {
      console.error('Error uploading PDF:', error);
      setMessage('Error uploading PDF');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-box">
        <h2>Upload Your PDF</h2>
        <div className="file-input-wrapper">
          <input 
            type="file" 
            onChange={handleFileChange} 
            accept=".pdf"
            id="file-input"
            className="file-input"
          />
          <label htmlFor="file-input" className="file-label">
            {file ? file.name : 'Choose a PDF file'}
          </label>
        </div>
        <button 
          className="upload-button" 
          onClick={handleUpload}
          disabled={!file || isLoading}
        >
          {isLoading ? 'Uploading...' : 'Upload PDF'}
        </button>
        {isLoading && <div className="loading">Loading, please wait...</div>}
        {message && <div className="message">{message}</div>}
      </div>
    </div>
  );
};

export default UploadPDF;
