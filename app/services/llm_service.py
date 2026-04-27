import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

MODEL_NAME = "gemini-2.5-flash"


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment.")
    return genai.Client(api_key=api_key)


def generate_llm_response(prompt: str) -> str:
    client = get_gemini_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text.strip() if response.text else ""