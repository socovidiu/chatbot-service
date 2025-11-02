import asyncio
from typing import Any
from schemas.chat_schema import ChatRequest

class LLMOperator:
    def __init__(self, llm: Any):
        self.llm = llm

    def build_prompt(self, req: ChatRequest) -> str:
        profile = req.profile or ""
        return (
            "You are a resume advisor. Given the user's message and profile, "
            "provide tailored suggestions to improve their CV.\n\n"
            f"Profile:\n{profile}\n\n"
            f"User question:\n{req.message}\n\n"
            "Return concise suggestions and sample bullet points."
        )

    async def generate(self, req: ChatRequest) -> str:
        prompt = self.build_prompt(req)
        # async call
        msg = await self.llm.ainvoke(prompt)
        return msg.content
    
