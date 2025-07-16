import os
from src.agents.characters.base_character import BaseCharacter
from src.infra.meta_io import MetaIO
from src.infra.supabase_client import SupabaseClient
from src.models.user import User
from src.agents.characters.characters import get_character

class MessageHandler:
    def __init__(self, local_mode = False):
        self.local_mode = local_mode
        self.db_client = SupabaseClient(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"), local_mode)
        self.meta_io = MetaIO(access_token=os.getenv("META_IO_ACCESS_TOKEN"), 
                              template_access_token=os.getenv("META_IO_TEMPLATE_ACCESS_TOKEN"), 
                              phone_number_id=os.getenv("META_IO_PHONE_NUMBER_ID"), 
                              db_client=self.db_client, 
                              local_mode=local_mode)


    def handle_message(self, user: User, message: str, character_name: str) -> str:
        character = get_character(character_name, self.meta_io, self.db_client)
        if character is None:
            return "Character not found"
        
        return character.process_message(user, message)
    