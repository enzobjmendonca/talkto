from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

USER_TABLE_CREATION_QUERY = """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    phone_number TEXT NOT NULL UNIQUE,
    current_character TEXT,
    resume TEXT,
    last_message_time TIMESTAMP WITH TIME ZONE,
    timezone TEXT
);

-- Indexes for performance
CREATE INDEX idx_users_phone_number ON users(phone_number);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_last_message_time ON users(last_message_time);
"""

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
    timezone: Optional[str] = None
    
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
            last_message_time=data['last_message_time'],
            timezone=data['timezone'])
        
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'phone_number': self.phone_number,
            'current_character': self.current_character,
            'resume': self.resume,
            'last_message_time': self.last_message_time,
            'timezone': self.timezone}
    