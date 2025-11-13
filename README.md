# E-Commerce NL→SQL Agent

An AI-powered tool that allows you to query an e-commerce SQLite database using natural language.  
It converts plain English questions into SQL queries and returns the results, with memory support for conversations.

---

## 🔹 Features

- Natural language → SQL query conversion using **OpenAI GPT-4o-mini**.
- Memory of previous conversations per session.
- Safe SQL execution (only `SELECT` queries allowed).
- Limit enforcement to avoid massive query results.
- Streamlit-based frontend for interactive use.
- FastAPI backend serving the API endpoints.

---

## 🔹 Tech Stack

- **Backend:** Python, FastAPI, SQLite
- **Frontend:** Streamlit
- **AI Model:** OpenAI GPT-4o-mini
- **Other Libraries:** `requests`, `pydantic`, `python-dotenv`, `sqlite3`
- **Middleware:** CORS via `starlette.middleware.cors`

---

## 🔹 Folder Structure

maersk-genai-agent/
├─ backend/
│ ├─ main.py # FastAPI server
│ ├─ sql_utils.py # SQLite utility functions
├─ frontend/
│ ├─ app.py # Streamlit frontend
├─ data/
│ ├─ ecommerce.db # SQLite database
├─ .env # Environment variables (OpenAI key, DB path)
├─ requirements.txt # Python dependencies
├─ README.md



---

##  Setup & Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ecommerce-nl-sql-agent.git
cd ecommerce-nl-sql-agent

```
2. **Create a virtual environment:**
```
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

```
3.**Install dependencies:**
```
pip install -r requirements.txt

```

4.**Add your .env file:**
```
OPENAI_API_KEY=your_openai_key_here
DB_PATH=./data/ecommerce.db
OPENAI_MODEL=gpt-4o-mini
```

## Running the Application

**Start the FastAPI backend:**
```
uvicorn backend.main:app --reload
```

**Start the Streamlit frontend:**
```
streamlit run frontend/app.py
```

Access the frontend at: http://localhost:8501

##🔹 API Endpoints

GET /health → Health check

POST /query → Convert a prompt into SQL and execute
```
Request JSON:

{
  "prompt": "Top 10 products by sales",
  "conversation_id": "optional-conversation-id",
  "limit": 100
}

```
##🔹 Security & Safety

Only SELECT statements are allowed.

Query results are limited via LIMIT clause.

Conversation memory stored locally in SQLite.
