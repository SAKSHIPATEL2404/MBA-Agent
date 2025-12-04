
import os
import requests
from typing import Optional, List, Dict

class LLM:
    """
    Wrapper for OpenRouter LLM API
    """

    def __init__(self, model=None):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("❌ ERROR: OPENROUTER_API_KEY missing in environment variables!")

       
        self.model = model or os.getenv("LLM_MODEL", "meta-llama/llama-3-70b-instruct")

      
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

       
        self.DEFAULT_SYSTEM_PROMPT = (
            "You are MBA-Agent — a friendly, smart, and practical business advisor. "
            "Give clear, structured, actionable answers."
        )

    def chat(
        self,
        user_messages: List[Dict],
        temperature: float = 0.2,
        max_tokens: int = 600,
        system_override: Optional[str] = None
    ):
        """
        Sends conversation to OpenRouter and returns the assistant response.
        """

        
        system_prompt = system_override or self.DEFAULT_SYSTEM_PROMPT

        messages = [{"role": "system", "content": system_prompt}] + user_messages

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "MBA-Agent",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            r = requests.post(self.base_url, headers=headers, json=payload, timeout=25)

            if r.status_code != 200:
                return {
                    "error": True,
                    "msg": f"❌ OpenRouter Error {r.status_code}: {r.text}"
                }

            data = r.json()

            if "choices" not in data or len(data["choices"]) == 0:
                return {"error": True, "msg": "❌ Empty response from LLM."}

            text = data["choices"][0]["message"].get("content", "")

            return {"error": False, "text": text}

        except requests.exceptions.Timeout:
            return {"error": True, "msg": "⚠ LLM request timed out."}

        except Exception as e:
            return {"error": True, "msg": f"❌ Exception: {str(e)}"}









