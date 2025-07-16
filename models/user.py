from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class User:
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    phone_number: str
    current_character: Optional[str] = None
    resume: Optional[str] = None
    last_message_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.last_message_time is None:
            self.last_message_time = datetime.now()


    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            id=data['id'],
            is_active=data['is_active'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            phone_number=data['phone_number'],
            current_character=data['current_character'],
            resume=data['resume'],
            last_message_time=data['last_message_time'])
        
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'phone_number': self.phone_number,
            'current_character': self.current_character,
            'resume': self.resume,
            'last_message_time': self.last_message_time}
    