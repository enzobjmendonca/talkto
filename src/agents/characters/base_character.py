from src.agents.base_agent import BaseAgent
from src.infra.meta_io import MetaIO
from src.infra.supabase_client import SupabaseClient
from src.models.user import User

class BaseCharacter(BaseAgent):
    def __init__(self, name: str, prompt: str, meta_io: MetaIO, db_client: SupabaseClient):
        super().__init__(name, prompt)
        self.meta_io = meta_io
        self.db_client = db_client

    def process_message(self, user: User, message: str) -> str:
        """
        Process a message from a user and return a response as the character.
        
        Args:
            user (User): The user sending the message
            message (str): The message content
            
        Returns:
            str: The character's response
        """
        # Get conversation history
        conversation_history = self.db_client.get_messages_for_openai(user.id, limit=10)
        
        # Build the system message with character prompt
        system_message = {
            "role": "system",
            "content": self.prompt
        }
        
        # Add conversation history
        messages = [system_message] + conversation_history
        
        # Add the current user message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Get AI completion
        try:
            response = self.get_completion(messages)
            return response
        except Exception as e:
            print(f"Error getting AI completion: {e}")
            return f"Desculpe, {self.name} está temporariamente indisponível. Tente novamente em alguns momentos."