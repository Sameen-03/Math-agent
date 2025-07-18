import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResponse(null);
    try {
      const res = await axios.post(`${API_URL}/query`, { question });
      setResponse(res.data);
    } catch (err) {
      setError(err.response ? err.response.data.detail : 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!feedback) return;
    try {
      const res = await axios.post(`${API_URL}/feedback`, { feedback });
      setResponse(prev => ({ ...prev, answer: res.data.refined_answer }));
      setFeedback('');
    } catch (err) {
      setError('Failed to submit feedback.');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧮 Math Routing Agent</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a math question..."
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </form>

        {error && <p className="error">{error}</p>}

        {response && (
          <div className="response-container">
            <h3>Answer</h3>
            <p className="source">Source: {response.source}</p>
            <pre>{response.answer}</pre>

            <div className="feedback-section">
              <h4>Was this helpful? Provide feedback to refine the answer.</h4>
              <form onSubmit={handleFeedbackSubmit}>
                <input
                  type="text"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="e.g., 'Explain the second step in more detail.'"
                />
                <button type="submit">Refine</button>
              </form>
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
