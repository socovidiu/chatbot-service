from fastapi import FastAPI
from api import chat, resume
from core.config import settings

app = FastAPI(title="Resume Chatbot API", description="API for generating resume suggestions using a chatbot.", version="1.0")

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(resume.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Chatbot API. Use the /chat endpoint to interact with the chatbot."}

export_app = app