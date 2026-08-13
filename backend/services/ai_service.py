import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class AIService:
    """Central service for TicketGenie's GPT model."""

    def __init__(self):
        self.client = None
        self.model = "gpt-5.2"

    def _get_client(self) -> OpenAI:
        if self.client is not None:
            return self.client

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

        if endpoint.endswith("/responses"):
            base_url = endpoint.removesuffix("responses")
        else:
            base_url = endpoint.rstrip("/") + "/"

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        return self.client

    def generate(
        self,
        *,
        system_prompt: str,
        user_content: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        """
        Send a structured request to GPT-5.2 and parse the response
        directly into the requested Pydantic model.
        """

        client = self._get_client()

        response = client.responses.parse(
            model=self.model,
            instructions=system_prompt,
            input=user_content,
            text_format=response_model,
        )

        return response.output_parsed


ai_service = AIService()