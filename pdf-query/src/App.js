import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadPDF from './components/UploadPDF';
import QueryPDF from './components/QueryPDF';
import Home from './components/Home';

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/embed" element={<UploadPDF />} />
          <Route path="/query" element={<QueryPDF />} />
          <Route path="/" element={<Home />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
