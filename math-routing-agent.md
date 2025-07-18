
# Math Routing Agent 🧠

This project is an **Agentic-RAG (Retrieval-Augmented Generation)** system designed to function as an AI-powered mathematics professor. It intelligently answers mathematical questions by either retrieving information from a dedicated knowledge base or searching the web. The agent includes AI guardrails for safety and a human-in-the-loop mechanism to learn from user feedback.

---

## 🔍 Features

- **Intelligent Routing**: The agent dynamically decides whether to use its internal knowledge base or perform a web search to find the best answer for a given question.

- **AI Guardrails**: An AI Gateway moderates all inputs and outputs, ensuring questions are math-related and that answers are safe and on-topic.

- **Vector Knowledge Base**: Uses Qdrant to store and retrieve existing math problems and solutions, acting as the agent's long-term memory.

- **Live Web Search**: Leverages the Tavily AI API to find up-to-date information online for questions not covered in the knowledge base.

- **Human-in-the-Loop Feedback**: Users can provide feedback on answers, which the agent uses to refine its response, enabling a self-correction and learning loop.

- **Structured Context (MCP)**: Implements the Model Context Protocol (MCP) by passing a structured state object through the entire workflow, ensuring every component has full context.

---

## 🧰 Tech Stack

- **Backend**: Python, FastAPI  
- **Frontend**: React  
- **AI Agent Framework**: LangGraph  
- **LLM**: Google Gemini 1.5 Pro  
- **Vector Database**: Qdrant  
- **Web Search Tool**: Tavily AI  
- **Embeddings**: Hugging Face Sentence Transformers

---

## 📁 Project Structure

```
math-routing-agent/
├── backend/
│   ├── app/
│   │   ├── agent.py         # The core LangGraph agent workflow
│   │   ├── feedback.py      # Human-in-the-loop refinement logic
│   │   ├── guardrails.py    # AI Gateway for moderation
│   │   ├── main.py          # FastAPI server and API endpoints
│   │   └── schemas.py       # Pydantic data models (for MCP)
│   ├── data/
│   │   └── math_dataset.json # The knowledge base source file
│   ├── scripts/
│   │   └── setup_knowledge_base.py # Script to create the VectorDB
│   ├── run_benchmark.py     # Script for JEE Bench evaluation
│   └── .env                 # API keys and environment variables
└── frontend/
    ├── src/
    │   └── App.js           # Main React component for the UI
    └── ...                  # Other standard React files
```

---

## 🚀 Setup and Installation

### ✅ Prerequisites

- Python 3.8+  
- Node.js and npm

---

### 🖥️ Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv venv
.env\Scriptsctivate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Set up API Keys:

1. Create a file named `.env` in the `backend` directory.  
2. Add your API keys:

```env
TAVILY_API_KEY="your_tavily_api_key"
GOOGLE_API_KEY="your_google_api_key"
```

Build the Knowledge Base:

1. Place your `math_dataset.json` file in the `backend/data/` folder.  
2. Run the setup script to populate the Qdrant database:

```bash
cd scripts
python setup_knowledge_base.py
cd ..
```

---

### 🌐 Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install Node.js dependencies:

```bash
npm install
```

---

## ▶️ How to Run the Application

First and foremost, we need to setup the knowledge base

Go to backend/scripts and run the file "setup_knowledge_base.py" to build the vector db

### 🔧 Start the Backend Server:

In a terminal, navigate to the `backend` directory and run:

```bash
uvicorn app.main:app --reload
```

The server will be running at:  
**http://localhost:8000**

---

### 💻 Start the Frontend Application:

In a separate terminal, navigate to the `frontend` directory and run:

```bash
npm start
```

Your browser will automatically open to:  
**http://localhost:3000**, where you can interact with the agent.

---
