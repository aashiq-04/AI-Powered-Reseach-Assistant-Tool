const API_URL = 'http://localhost:8000';

export const apiService = {
  async embedDocuments() {
    const response = await fetch(`${API_URL}/embed`, {
      method: 'POST',
    });
    return response.json();
  },

  async queryDocuments(question) {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });
    return response.json();
  }
}; 