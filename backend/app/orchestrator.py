from typing import Dict, List, Optional, AsyncGenerator
from app.llm import LLM
import asyncio

class Orchestrator:
    """
    Main controller that manages:
    - Chat sessions (per chat_id)
    - Personality modes
    - System prompts
    - Routing messages to LLM
    """

    def __init__(self):
        self.llm = LLM()

       
        self.sessions: Dict[str, List[Dict]] = {}

    
        self.PERSONA_PROMPTS = {
            "default": """
You are MBA-Agent — a sharp, friendly, modern business assistant.
Respond in 3–6 lines. Be clear, helpful, and to the point.
Do NOT add Summary / Breakdown / Steps unless the user asks.
""",
            "mba_coach": """
You are an MBA Admission Coach.
Your tone is supportive, clear and motivational.
Help with essays, interviews, goals and clarity.
Keep responses short (4–7 lines).
""",
            "investor": """
You are an Investor Analyst focusing on ROI, strategy, competition,
unit economics, and risks. Be sharp, structured and concise.
Use bullet points where helpful.
""",
            "startup": """
You are a Startup Growth Hacker.
Give fast, high-impact solutions. Focus on execution.
Keep responses crisp, energetic, and practical.
"""
        }

   
    def _ensure_session(self, chat_id: str):
        if chat_id not in self.sessions:
            self.sessions[chat_id] = []

    
    async def handle_message(
        self,
        user_id: str,
        message: str,
        persona: Optional[str] = "default",
        chat_id: Optional[str] = None
    ) -> str:

        if not chat_id:
            chat_id = user_id  

        self._ensure_session(chat_id)

       
        self.sessions[chat_id].append({"role": "user", "content": message})

        system_prompt = self.PERSONA_PROMPTS.get(persona, self.PERSONA_PROMPTS["default"])

       
        response = self.llm.chat(
            user_messages=self.sessions[chat_id],
            system_override=system_prompt
        )

        if response.get("error"):
            answer = f"⚠️ {response['msg']}"
        else:
            answer = response["text"]

        
        self.sessions[chat_id].append({"role": "assistant", "content": answer})

        return answer

    async def stream_reply(
        self,
        user_id: str,
        message: str,
        persona: Optional[str] = "default",
        chat_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:

        if not chat_id:
            chat_id = user_id

        self._ensure_session(chat_id)
        self.sessions[chat_id].append({"role": "user", "content": message})

        system_prompt = self.PERSONA_PROMPTS.get(persona, self.PERSONA_PROMPTS["default"])

        response = self.llm.chat(
            user_messages=self.sessions[chat_id],
            system_override=system_prompt
        )

        if response.get("error"):
            yield "⚠️ " + response["msg"]
            return

        full_text = response.get("text", "")
        CHUNK_SIZE = 20
        idx = 0

        while idx < len(full_text):
            chunk = full_text[idx: idx + CHUNK_SIZE]
            idx += CHUNK_SIZE
            await asyncio.sleep(0.03)
            yield chunk

        self.sessions[chat_id].append({"role": "assistant", "content": full_text})

    def reset_session(self, chat_id: str):
        self.sessions[chat_id] = []
