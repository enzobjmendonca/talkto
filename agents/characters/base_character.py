from abc import ABC, abstractmethod

class BaseCharacter(ABC):
    def __init__(self, name: str, prompt: str):
        self.name = name
        self.prompt = prompt

    @abstractmethod
    def get_response(self, user_input: str) -> str:
        pass