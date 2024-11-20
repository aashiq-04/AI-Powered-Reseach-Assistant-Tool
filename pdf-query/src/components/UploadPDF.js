import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const UploadPDF = () => {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [isEmbedEnabled, setIsEmbedEnabled] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setIsEmbedEnabled(false);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("pdf", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      console.log("Response:", response);

      if (!response.ok) {
        const errorData = await response.json();
        setMessage(
          `Error uploading PDF: ${errorData.detail || "Unknown error"}`
        );
        setIsEmbedEnabled(false);
        return;
      }

      const data = await response.json();
      setMessage(data.message || "File uploaded successfully!");
      setIsEmbedEnabled(true);
    } catch (error) {
      console.error("Error uploading PDF:", error);
      setMessage("Error uploading PDF");
      setIsEmbedEnabled(false);
    }
  };

  const handleEmbed = async () => {
    setIsLoading(true);
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/embed", {
        method: "POST",
      });

      console.log("Response:", response);

      if (!response.ok) {
        const errorData = await response.json();
        setMessage(
          `Error embedding documents: ${errorData.message || "Unknown error"}`
        );
        return;
      }

      const data = await response.json();
      setMessage(data.message || "Embedding process completed successfully!");
      navigate("/query");
    } catch (error) {
      console.error("Error embedding documents:", error);
      setMessage("Error embedding documents");
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
            {file ? file.name : "Choose a PDF file"}
          </label>
        </div>
        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={!file || isLoading}
        >
          {isLoading ? "Uploading..." : "Upload PDF"}
        </button>
        <button
          className="embed-button"
          onClick={handleEmbed}
          disabled={isLoading || !isEmbedEnabled}
        >
          {isLoading ? "Embedding..." : "Start Embedding"}
        </button>
        {isLoading && (
          <div className="loading">Loading document, please wait...</div>
        )}
        {message && <div className="message">{message}</div>}
      </div>
    </div>
  );
};

export default UploadPDF;
