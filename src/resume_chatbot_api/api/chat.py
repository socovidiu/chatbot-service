# api/chat.py
from fastapi import APIRouter, HTTPException
from schemas.chat_schema import ChatRequest, ChatResponse, ResumeSuggestion
from services.llm_operator import LLMOperator
from core.config import settings

router = APIRouter()
llm = LLMOperator(settings.create_chat_llm())

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        text = await llm.generate(request)
        return ChatResponse(
            original=request,
            suggestion=ResumeSuggestion(raw_text=text)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
