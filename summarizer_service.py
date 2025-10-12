import os
from typing import Optional
import httpx


class NotesSummarizerService:
    """Service for summarizing extracted text from notes."""

    def __init__(self):
        self.api_key = os.getenv("SUMMARY_API_KEY")
        self.provider = os.getenv("SUMMARY_API_PROVIDER", "openai")
        self.model = os.getenv("SUMMARY_MODEL", "gpt-3.5-turbo")

    async def summarize(self, text: str, prompt: Optional[str] = None) -> Optional[str]:
        """
        Summarize the given text into short, student-friendly bullet points.

        Returns None if the provider or API key is not configured.
        """
        if not self.api_key:
            return None

        if self.provider.lower() == "openai":
            return await self._summarize_with_openai(text, prompt)

        # Unknown provider
        return None

    async def _summarize_with_openai(self, text: str, prompt: Optional[str] = None) -> Optional[str]:
        """Use OpenAI Chat Completions API via httpx (no SDK dependency)."""
        try:
            # Truncate overly long texts to keep request size reasonable
            max_chars = int(os.getenv("SUMMARY_MAX_INPUT_CHARS", "12000"))
            payload_text = text[:max_chars]

            # Use caller-supplied prompt if provided; otherwise default concise study prompt
            system_prompt = (
                prompt
                or (
                    "You are a helpful study assistant. Summarize the user's notes into a very "
                    "concise, student-friendly study summary using 5-10 bullet points or short "
                    "paragraphs. Keep language simple, highlight key definitions, formulas, and "
                    "must-know facts. Avoid fluff."
                )
            )

            body = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": payload_text},
                ],
                "temperature": 0.3,
                "max_tokens": 500,
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=body,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                return content or None
        except Exception:
            return None


