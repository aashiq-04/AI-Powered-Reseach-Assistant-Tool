import React, { useState } from "react";
import { apiService } from "../services/api";

const QueryPDF = () => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiService.queryDocuments(question);
      setAnswer(data.answer);
    } catch (err) {
      setError('Failed to get answer. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="home-container">
      <nav className='navigation'>
        <div className='al'>
          <a className='homeLink' href="/">Home</a>
          <a className='aboutLink' href="/">About</a>
        </div>
      </nav>
      <h1 className='head1'>Query Your PDF</h1>
      <div className="Div-al">
      <form onSubmit={handleSubmit}>
        <input
        className="ques"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask your question..."
        />
        <button className="subBut" type="submit" disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Ask'}
        </button>
      </form>
      </div>
      
      {error && <div className="error">{error}</div>}
      {answer && (
        <div className="answer">
          <h3>Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default QueryPDF;
