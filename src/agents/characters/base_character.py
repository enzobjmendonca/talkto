from src.agents.base_agent import BaseAgent

class BaseCharacter(BaseAgent):
    def __init__(self, name: str, prompt: str, meta_io: MetaIO, db_client: Supabase):
        self.name = name
        self.prompt = prompt
        self.meta_io = meta_io
        self.db_client = db_client

    def process_message(self, user: User, message: str) -> str:
        pass