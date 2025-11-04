# services/llm_operator.py
from __future__ import annotations
from typing import Any, Dict, Optional, Union
import json, re

from langchain_core.messages import SystemMessage, HumanMessage
from . import prompt_builders as pb

class LLMOperator:
    def __init__(self, chat_llm: Any):
        self.llm = chat_llm

    async def _ainvoke_text(self, system: str, user: str) -> str:
        msgs = [SystemMessage(content=system.strip()), HumanMessage(content=user.strip())]
        resp = await self.llm.ainvoke(msgs)
        return getattr(resp, "content", str(resp))

    async def _invoke_json(self, system: str, user: str, schema_hint: Optional[str]) -> Dict[str, Any]:
        guard = (
            "\n\nReturn ONLY valid JSON that matches the schema. "
            "No backticks, no markdown, no extra commentary."
        )
        if schema_hint:
            guard += f"\nJSON schema (shape): {schema_hint}"

        raw = await self._ainvoke_text(system, user + guard)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}|\[.*\]", raw, re.S)
            if not m:
                raise ValueError(f"Model did not return JSON: {raw[:300]}")
            return json.loads(m.group(0))

    # ---- Public tasks (thin wrappers) ----
    async def analyze_profile(self, profile: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        system, user, schema = pb.analyze_profile(profile)
        return await self._invoke_json(system, user, schema)

    async def extract_keywords(self, jd: str) -> Dict[str, Any]:
        system, user, schema = pb.extract_keywords(jd)
        return await self._invoke_json(system, user, schema)

    async def tailor_bullets(self, profile: Dict[str, Any], jd: str, tone: str = "concise") -> Dict[str, Any]:
        system, user, schema = pb.tailor_bullets(profile, jd, tone)
        return await self._invoke_json(system, user, schema)

    async def write_summary(self, profile: Dict[str, Any], jd: Optional[str]) -> Dict[str, Any]:
        system, user, schema = pb.write_summary(profile, jd)
        return await self._invoke_json(system, user, schema)

    async def write_cover_letter(self, profile: Dict[str, Any], jd: str, company: Optional[str], role: Optional[str]) -> Dict[str, Any]:
        system, user, schema = pb.write_cover_letter(profile, jd, company, role)
        return await self._invoke_json(system, user, schema)

    async def ats_score(self, resume_text: str, jd: str) -> Dict[str, Any]:
        system, user, schema = pb.ats_score(resume_text, jd)
        return await self._invoke_json(system, user, schema)
