from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pytz
from supabase import create_client, Client
from src.models.user import User
from src.models.message import Message
from src.infra.local_cache import cached

class SupabaseClient:
    """
    Handles database operations using Supabase or local in-memory storage.
    
    This class provides functionality for interacting with the Supabase database,
    including user management, prayer plan operations, and caching. It implements
    methods for CRUD operations on users and prayer plans, with built-in caching
    for frequently accessed data.
    
    Attributes:
        client (Client): Supabase client instance for database operations (None in local mode)
        local_mode (bool): Whether to use local in-memory storage
        local_users (Dict): Local storage for users
        local_messages (Dict): Local storage for messages
        next_user_id (int): Next available user ID for local mode
        next_message_id (int): Next available message ID for local mode
    """
    
    def __init__(self, url: str = None, key: str = None, local_mode: bool = False):
        """
        Initialize the Supabase client.
        
        Args:
            url (str): Supabase project URL (ignored in local mode)
            key (str): Supabase API key (ignored in local mode)
            local_mode (bool): Whether to use local in-memory storage
        """
        self.local_mode = local_mode
        
        if local_mode:
            self.client = None
            self.local_users = {}
            self.local_messages = {}
            self.next_user_id = 1
            self.next_message_id = 1
        else:
            if not url or not key:
                raise ValueError("URL and key are required when not in local mode")
            self.client: Client = create_client(url, key)

    @cached()
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.
        
        This method is cached to improve performance for frequently accessed users.
        
        Args:
            user_id (int): The ID of the user to retrieve
            
        Returns:
            Optional[User]: User data if found, None otherwise
        """
        if self.local_mode:
            return self.local_users.get(user_id)
        
        response = self.client.table('users').select('*').eq('id', user_id).execute()
        if response.data:
            return User.from_dict(response.data[0])
        return None

    @cached()
    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """
        Retrieve a user by their phone number.
        
        This method is cached to improve performance for frequently accessed users.
        
        Args:
            phone_number (str): The phone number of the user to retrieve
            
        Returns:
            Optional[User]: User data if found, None otherwise
        """
        if self.local_mode:
            for user in self.local_users.values():
                if user.phone_number == phone_number:
                    return user
            return None
        
        response = self.client.table('users').select('*').eq('phone_number', phone_number).execute()
        if response.data:
            return User.from_dict(response.data[0])
        return None

    def save_user(self, user: User, cache_only: bool = False) -> None:
        """
        Save user data to the database and update cache.
        
        This method:
        1. Optionally saves user data to the database
        2. Updates the cache with the latest user data
        
        Args:
            user (User): The user data to save
            cache_only (bool): If True, only update cache without database write
        """
        if self.local_mode:
            if not cache_only:
                self.local_users[user.id] = user
        else:
            if not cache_only:
                self.client.table('users').upsert(user.to_dict()).execute()
        
        self._update_cache(user)

    def _update_cache(self, user: User) -> None:
        """
        Update cache entries for a user.
        
        This method updates both the ID-based and phone-based cache entries
        for a user to maintain cache consistency.
        
        Args:
            user (User): The user data to cache
        """
        # Update cache for get_user
        cache_key = f"get_user:{str((user.id,))}"
        self.get_user.cache.set(cache_key, user)
        
        # Update cache for get_user_by_phone
        cache_key = f"get_user_by_phone:{str((user.phone_number,))}"
        self.get_user_by_phone.cache.set(cache_key, user)

    def get_active_users(self) -> List[User]:
        """
        Retrieve all active users from the database.
        
        Returns:
            List[User]: List of all active users
        """
        if self.local_mode:
            return [user for user in self.local_users.values() if user.is_active]
        
        response = self.client.table('users').select('*').eq('is_active', True).execute()
        users = [User.from_dict(user_data) for user_data in response.data]
        return users

    def get_users_near_24h_inactive(self, window_minutes: int = 5) -> List[User]:
        """
        Retrieve users who are about to complete 24 hours without interaction.
        
        This method finds users whose last_message_time is within a specific window
        before completing 24 hours of inactivity. For example, with window_minutes=5,
        it finds users who will complete 24h of inactivity in the next 5 minutes.
        
        Args:
            window_minutes (int): Time window in minutes before 24h completion
            
        Returns:
            List[User]: Users approaching 24h inactivity threshold
        """
        try:
            # Calculate time boundaries
            # Ensure all datetime comparisons are done in UTC, since Supabase stores timestamps in UTC.
            now = datetime.now(pytz.utc)
            
            # Target time: exactly 24h ago + window (when they'll hit 24h)
            twenty_four_hours_ago = now - timedelta(hours=24)
            window_start = twenty_four_hours_ago + timedelta(minutes=window_minutes)
            window_end = twenty_four_hours_ago

            # Convert window to UTC for the query.
            window_start = window_start.astimezone(pytz.utc)
            window_end = window_end.astimezone(pytz.utc)
            
            if self.local_mode:
                users = []
                for user in self.local_users.values():
                    if user.last_message_time:
                        # Convert to UTC for comparison
                        last_msg_time = user.last_message_time
                        if last_msg_time.tzinfo is None:
                            last_msg_time = pytz.utc.localize(last_msg_time)
                        else:
                            last_msg_time = last_msg_time.astimezone(pytz.utc)
                        
                        if window_end <= last_msg_time < window_start:
                            users.append(user)
                return users
            
            # Query users with last_message_time in the target window
            response = self.client.table('users')\
                .select('*')\
                .gte('last_message_time', window_end.isoformat())\
                .lt('last_message_time', window_start.isoformat())\
                .execute()
            
            users = [User.from_dict(user_data) for user_data in response.data]
            
            return users
            
        except Exception as e:
            return []

    def create_user(self, phone_number: str) -> User:
        """
        Create a new user in the database.
        
        This method:
        1. Creates a new User instance with default values
        2. Inserts the user into the database
        3. Returns the created user with its database ID
        
        Args:
            phone_number (str): The phone number for the new user
            
        Returns:
            User: The newly created user
        """
        new_user = User(
            id=0,  # Will be set by database
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            phone_number=phone_number,
            current_character=None,
            resume=None,
            last_message_time=datetime.now(),
            timezone="America/Sao_Paulo"
        )
        
        if self.local_mode:
            new_user.id = self.next_user_id
            self.next_user_id += 1
            self.local_users[new_user.id] = new_user
            return new_user
        
        response = self.client.table('users').insert(new_user.to_dict()).execute()
        user = User.from_dict(response.data[0])
        return user

    def clear_cache(self) -> None:
        """A function to clear the lru cache, needs to be run after a manual update in the db"""
        self.get_user.cache.clear()
        self.get_user_by_phone.cache.clear()

    # =================== MESSAGE OPERATIONS ===================

    def append_message(self, user_id: int, role: str, content: Optional[str] = None, 
                      function_call: Optional[Dict[str, Any]] = None, 
                      function_name: Optional[str] = None) -> Message:
        """
        Append a new message to the user's conversation history.
        
        Args:
            user_id (int): ID of the user
            role (str): Role of the message ('user', 'assistant', 'function')
            content (Optional[str]): Message content
            function_call (Optional[Dict]): Function call data for assistant messages
            function_name (Optional[str]): Function name for function messages
            
        Returns:
            Message: The created message
        """
        try:
            # Get current message count for indexing
            current_count = self.get_message_count(user_id)
            
            message = Message(
                user_id=user_id,
                role=role,
                content=content,
                function_call=function_call,
                function_name=function_name,
                message_index=current_count + 1
            )
            
            if self.local_mode:
                message.id = self.next_message_id
                self.next_message_id += 1
                if user_id not in self.local_messages:
                    self.local_messages[user_id] = []
                self.local_messages[user_id].append(message)
                return message
            
            response = self.client.table('messages').insert(message.to_dict()).execute()
            created_message = Message.from_dict(response.data[0])
            
            return created_message
            
        except Exception as e:
            raise

    def get_recent_messages(self, user_id: int, limit: int = 10) -> List[Message]:
        """
        Get the most recent messages for a user.
        
        Args:
            user_id (int): ID of the user
            limit (int): Number of messages to retrieve (default 10)
            
        Returns:
            List[Message]: List of recent messages, newest first
        """
        try:
            if self.local_mode:
                if user_id not in self.local_messages:
                    return []
                messages = sorted(self.local_messages[user_id], key=lambda x: x.message_index, reverse=True)[:limit]
                # Return in chronological order (oldest first)
                messages.reverse()
                return messages
            
            response = self.client.table('messages')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('message_index', desc=True)\
                .limit(limit)\
                .execute()
            
            messages = [Message.from_dict(msg_data) for msg_data in response.data]
            # Return in chronological order (oldest first)
            messages.reverse()
            
            return messages
            
        except Exception as e:
            return []

    def get_messages_for_openai(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages formatted for OpenAI API.
        
        Args:
            user_id (int): ID of the user
            limit (int): Number of messages to retrieve
            
        Returns:
            List[Dict]: Messages in OpenAI format
        """
        messages = self.get_recent_messages(user_id, limit)
        return [msg.to_openai_format() for msg in messages]

    def get_message_count(self, user_id: int) -> int:
        """
        Get total message count for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            int: Total number of messages
        """
        try:
            if self.local_mode:
                return len(self.local_messages.get(user_id, []))
            
            response = self.client.table('messages')\
                .select('id', count='exact')\
                .eq('user_id', user_id)\
                .execute()
            
            return response.count or 0
            
        except Exception as e:
            return 0

    def clear_user_messages(self, user_id: int) -> bool:
        """
        Clear all messages for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            bool: True if successful
        """
        try:
            if self.local_mode:
                if user_id in self.local_messages:
                    del self.local_messages[user_id]
                return True
            
            self.client.table('messages').delete().eq('user_id', user_id).execute()
            return True
            
        except Exception as e:
            return False

    def get_conversation_summary(self, user_id: int, limit: int = 50) -> str:
        """
        Get a text summary of recent conversation for resume generation.
        
        Args:
            user_id (int): ID of the user
            limit (int): Number of recent messages to include
            
        Returns:
            str: Formatted conversation summary
        """
        messages = self.get_recent_messages(user_id, limit)
        
        conversation_lines = []
        for msg in messages:
            if msg.role == 'user':
                conversation_lines.append(f"User: {msg.content}")
            elif msg.role == 'assistant':
                if msg.content:
                    conversation_lines.append(f"Bot: {msg.content}")
                elif msg.function_call:
                    conversation_lines.append(f"Bot: [Action: {msg.function_call.get('name', 'unknown')}]")
            elif msg.role == 'function':
                conversation_lines.append(f"System: [Function result]")
        
        return '\n'.join(conversation_lines[-20:])  # Last 20 exchanges

    def reset_local_data(self) -> None:
        """
        Reset all local data (users and messages).
        Only available in local mode.
        """
        if not self.local_mode:
            raise ValueError("reset_local_data() is only available in local mode")
        
        self.local_users.clear()
        self.local_messages.clear()
        self.next_user_id = 1
        self.next_message_id = 1
        self.clear_cache()

    def get_local_stats(self) -> Dict[str, Any]:
        """
        Get statistics about local data.
        Only available in local mode.
        
        Returns:
            Dict containing user count, message count, and other stats
        """
        if not self.local_mode:
            raise ValueError("get_local_stats() is only available in local mode")
        
        total_messages = sum(len(messages) for messages in self.local_messages.values())
        active_users = len([user for user in self.local_users.values() if user.is_active])
        
        return {
            "total_users": len(self.local_users),
            "active_users": active_users,
            "total_messages": total_messages,
            "next_user_id": self.next_user_id,
            "next_message_id": self.next_message_id
        } 
    