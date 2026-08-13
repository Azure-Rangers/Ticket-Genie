import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class AIService:
    """Central service for TicketGenie's GPT model."""

    def __init__(self):
        api_key = os.getenv("GROUP1OPENAIAPIKEY")
        endpoint = os.getenv("GROUP1OPENAIENDPOINT")

        if not api_key:
            raise ValueError(
                "GROUP1OPENAIAPIKEY is missing. "
                "Run fetch_secrets.py to populate .env."
            )

        if not endpoint:
            raise ValueError(
                "GROUP1OPENAIENDPOINT is missing. "
                "Run fetch_secrets.py to populate .env."
            )

        # Key Vault stores the full Responses API endpoint.
        # The SDK needs the base /openai/v1/ URL.
        if endpoint.endswith("/responses"):
            base_url = endpoint.removesuffix("responses")
        else:
            base_url = endpoint.rstrip("/") + "/"

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        self.model = "gpt-5.2"

    def generate(self, prompt: str) -> str:
        """Send a prompt to GPT-5.2 and return its text response."""

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text.strip()


ai_service = AIService()