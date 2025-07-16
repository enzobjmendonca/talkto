from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

TABLE_CREATION_QUERY = """
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'function')),
    content TEXT,
    function_call JSONB,
    function_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_index INTEGER NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_user_created ON messages(user_id, created_at DESC);
CREATE INDEX idx_messages_user_index ON messages(user_id, message_index DESC);
"""

@dataclass
class Message:
    user_id: int
    role: str  # 'user', 'assistant', 'function'
    content: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    function_name: Optional[str] = None
    message_index: int = 0
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create Message instance from database dict."""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))

        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            role=data.get('role'),
            content=data.get('content'),
            function_call=data.get('function_call'),
            function_name=data.get('function_name'),
            message_index=data.get('message_index', 0),
            created_at=created_at
        )

    def to_dict(self) -> dict:
        """Convert Message to database dict."""
        data = {
            'user_id': self.user_id,
            'role': self.role,
            'content': self.content,
            'function_call': self.function_call,
            'function_name': self.function_name,
            'message_index': self.message_index
        }
        
        if self.id is not None:
            data['id'] = self.id
            
        if self.created_at is not None:
            data['created_at'] = self.created_at.isoformat()
            
        return data

    def to_openai_format(self) -> dict:
        """Convert Message to OpenAI chat format."""
        message = {
            "role": self.role,
            "content": self.content
        }
        
        if self.function_call:
            message["function_call"] = self.function_call
            
        if self.function_name:
            message["name"] = self.function_name
            
        return message 