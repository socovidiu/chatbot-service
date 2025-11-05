from fastapi import FastAPI, Depends
from api import chat, resume
from security.security import require_api_key

app = FastAPI(
    title="Resume Chatbot API", 
    description="API for generating resume suggestions using a chatbot.", 
    version="1.0",
    # Require API key for *every* endpoint (including /)
    dependencies=[Depends(require_api_key)],
    )

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(resume.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Chatbot API. Use the /chat endpoint to interact with the chatbot."}

export_app = app