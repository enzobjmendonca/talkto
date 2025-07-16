from abc import ABC, abstractmethod
from openai import OpenAI
import dotenv
import os
dotenv.load_dotenv()

class BaseAgent(ABC):
    def __init__(self, name: str, prompt: str, model: str = "gemini-2.5-flash", temperature: float = 0.5, max_tokens: int = 1000):
        self.name = name
        self.prompt = prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=os.getenv("AI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

    def get_completion(self, messages) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content