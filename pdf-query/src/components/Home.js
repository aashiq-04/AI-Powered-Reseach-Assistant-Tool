import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="home-container">
      <nav className='navigation'>
        <div className='al'>
        <a className='homeLink' href="/">Home</a>
        <a className='aboutLink' href="/">About</a>
        </div>
      </nav>
      <h1 className='head1'> AI Based Research Assistant Tool</h1>
      <div className="button-container">
        <Link to="/embed" className="nav-button">Upload PDF</Link>
        <Link to="/query" className="nav-button">Query PDF</Link>
      </div>
    </div>
  );
}

export default Home;