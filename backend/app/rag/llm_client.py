# app/rag/llm_client.py

import logging
import requests
from app.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Try new OpenAI API
try:
    from openai import OpenAI
    NEW_OPENAI = True
except ImportError:
    NEW_OPENAI = False
    import openai  # legacy API


class LLMClient:
    def __init__(self):
        self.use_openai = settings.openai_api_key is not None

        if self.use_openai:
            if NEW_OPENAI:
                self.client = OpenAI(api_key=settings.openai_api_key)
                logger.info("Using NEW OpenAI client")
            else:
                openai.api_key = settings.openai_api_key
                logger.info("Using LEGACY OpenAI client")

        else:
            logger.warning("No OPENAI_API_KEY set — using local LLM endpoint")
            self.client = None

    def generate(self, prompt: str) -> str:
        if self.use_openai:
            if NEW_OPENAI:
                return self._generate_new(prompt)
            else:
                return self._generate_legacy(prompt)

        return self._generate_local(prompt)

    # ----------------------------
    # New client
    # ----------------------------
    def _generate_new(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content

    # ----------------------------
    # Legacy client
    # ----------------------------
    def _generate_legacy(self, prompt: str) -> str:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message["content"]

    # ----------------------------
    # Local fallback LLM
    # ----------------------------
    def _generate_local(self, prompt: str) -> str:
        try:
            r = requests.post(
                settings.llm_endpoint,
                json={"prompt": prompt},
                timeout=settings.llm_timeout_seconds,
            )
            r.raise_for_status()
            return r.json().get("text", "")
        except Exception as e:
            return f"[LOCAL LLM ERROR] {e}"


_llm_client = None

def get_llm_client():
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
