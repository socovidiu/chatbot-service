# Resume Chatbot API

A FastAPI microservice for generating resume-building suggestions powered by LLM (Large Language Models) via LangChain.
The chatbot provides AI-assisted resume advice, improving and tailoring resumes based on user input and profiles.



## Features

- **Chatbot Interaction**: Users can converse with the AI for personalized resume guidance.
- **AI Suggestions**: Uses LangChain to interface with providers like OpenAI or Ollama.
- **Configurable LLM Backend**: Easily switch between openai or local ollama models.
- **Structured Schemas**: Pydantic models for requests, responses, and resume data.
- **API Endpoints**: The application exposes API endpoints for chatbot functionality.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd chatbot-service
   ```

2. Environment Setup:
You can use any Python environment manager.
This project uses uv for fast dependency management, but pip works as well.
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
   Or with uv:
   ```
   uv venv
   source .venv/bin/activate
   uv sync
   ```

3. Configure Environment Variables:
   ```
   cp .env.example .env
   ```
Environment variables include:
   ```
   LANGCHAIN_PROVIDER=openai   # or ollama
   OPENAI_API_KEY=sk-...
   MODEL=gpt-4o-mini
   OLLAMA_MODEL=llama3.2
   OLLAMA_BASE_URL=http://localhost:11434
   DEBUG=True
   LLM_TEMPERATURE=0.2
   ```

4. Run the application:
   Using uvicorn:
   ```
   uv run uvicorn app:app --reload
   ```
   Or using python:
   ```
   python main.py
   ```
Interactive docs available at: http://localhost:8000/docs

## Testing

To run the tests, use the following command:
```
uv run pytest -v
```
or 
```
pytest -v
```

## 🧠 LLM Provider Configuration

The API uses LangChain-compatible LLMs:
- OpenAI (LANGCHAIN_PROVIDER=openai)
- Ollama (local) (LANGCHAIN_PROVIDER=ollama)
Switch between providers via .env without code changes.