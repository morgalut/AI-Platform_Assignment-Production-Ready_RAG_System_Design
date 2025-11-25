# app/rag/llm_client.py

import requests
import openai
from app.config.settings import get_settings

settings = get_settings()


class LLMClient:
    def __init__(self):
        self.use_openai = settings.openai_api_key is not None

        if self.use_openai:
            openai.api_key = settings.openai_api_key

    def generate(self, prompt: str) -> str:
        if self.use_openai:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message["content"]

        # Fallback: call local LLM endpoint
        try:
            r = requests.post(
                settings.llm_endpoint,
                json={"prompt": prompt},
                timeout=settings.llm_timeout_seconds,
            )
            r.raise_for_status()
            return r.json().get("text", "")
        except Exception as e:
            return f"[LLM ERROR] {str(e)}"


_llm_client = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
