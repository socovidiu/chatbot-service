from fastapi import APIRouter, Depends, HTTPException
from schemas.chat_schema import ChatRequest, ChatResponse
from services.llm_operator import LLMOperator
from core.config import settings

router = APIRouter()

llm = LLMOperator(api_key=settings.LLM_API_KEY)

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Validate input similar to tests
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        prompt = llm.build_prompt(request)
        text = await llm.generate(prompt)
        return ChatResponse(original=request, suggestion=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest", response_model=ChatResponse)
async def suggest(request: ChatRequest):
    """
    Generate resume suggestions for a user message + optional profile/resume data.
    """
    try:
        prompt = llm.build_prompt(request)
        text = await llm.generate(prompt)
        return ChatResponse(original=request, suggestion=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
