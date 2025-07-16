#!/usr/bin/env python3
"""
Local Test Script for Message Handler Service

This script allows you to manually test the complete message handler flow
by inputting data yourself. It simulates the entire process from receiving
a message to sending a response.

Usage:
    python local_test.py
"""

import os
import sys
import dotenv
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
dotenv.load_dotenv()

from src.services.message_handler import MessageHandler
from src.infra.meta_io import MetaIO
from src.infra.supabase_client import SupabaseClient
from src.models.user import User
from src.agents.characters import get_available_characters, get_character_prompt

def main():
    """Main function for manual testing."""
    print("🚀 LOCAL TEST - Message Handler Service")
    print("=" * 50)
    print("This tool allows you to manually test the complete message flow.")
    print("You will input all data manually to simulate the real process.")
    print("=" * 50)
    
    # Initialize services in local mode
    print("\n📡 Initializing services in LOCAL MODE...")
    message_handler = MessageHandler(local_mode=True)
    print("✅ Services initialized successfully!")
    
    # Show available characters
    characters = get_available_characters()
    print(f"\n📚 Available characters ({len(characters)}):")
    for i, char in enumerate(characters, 1):
        print(f"{i:2d}. {char}")
    
    while True:
        print("\n" + "=" * 50)
        print("🔧 MANUAL TEST MENU")
        print("=" * 50)
        print("1. Test complete message flow")
        print("2. Create a new user")
        print("3. List existing users")
        print("4. Show conversation history")
        print("5. Show database stats")
        print("6. Reset all data")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            test_complete_flow(message_handler)
        elif choice == '2':
            create_user_manually(message_handler.db_client)
        elif choice == '3':
            list_users(message_handler.db_client)
        elif choice == '4':
            show_conversation_history(message_handler.db_client)
        elif choice == '5':
            show_stats(message_handler.db_client)
        elif choice == '6':
            reset_data(message_handler.db_client)
        elif choice == '7':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-7.")

def test_complete_flow(message_handler):
    """Test the complete message handling flow manually."""
    print("\n🔄 TESTING COMPLETE MESSAGE FLOW")
    print("=" * 50)
    
    # Step 1: Get or create user
    print("\n👤 STEP 1: User Information")
    try:
        phone_number = input("Enter phone number (e.g., +5511999999999): ").strip()
        
        if not phone_number:
            print("❌ Phone number is required!")
            return
        
        # Get or create user
        user = message_handler.db_client.get_user_by_phone(phone_number)
        if not user:
            print(f"📝 Creating new user with phone: {phone_number}")
            user = message_handler.db_client.create_user(phone_number)
            print(f"✅ User created: ID {user.id}")
        else:
            print(f"✅ Found existing user: ID {user.id}")
        
    except Exception as e:
        print(f"❌ Error in Step 1: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Select character
    print("\n🎭 STEP 2: Character Selection")
    try:
        characters = get_available_characters()
    
        for i, char in enumerate(characters, 1):
            print(f"{i:2d}. {char}")
        
        while True:
            try:
                char_choice = input(f"\nSelect character (1-{len(characters)}): ").strip()
                char_index = int(char_choice) - 1
                if 0 <= char_index < len(characters):
                    character_name = characters[char_index]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(characters)}")
            except ValueError:
                print("❌ Please enter a valid number")
    except Exception as e:
        print(f"❌ Error in Step 2: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"✅ Selected character: {character_name}")
    
    # NOVO: Loop de conversa contínua com o personagem
    print("\n💬 STEP 3: Conversa com o personagem (digite 'voltar' para sair)")
    while True:
        user_message = input("Você: ").strip()
        
        if user_message.lower() == "voltar":
            print("\n⬅️ Voltando ao menu principal...")
            break
        if not user_message:
            print("❌ Mensagem não pode ser vazia!")
            continue
        
        print(f"✅ User message: {user_message}")
        
        # Step 4: Process message
        try:
            # Save user message to database
            message_handler.db_client.append_message(user.id, "user", user_message)
            # Update user's last message time
            user.last_message_time = datetime.now()
            message_handler.db_client.save_user(user)
            # Get character response
            response = message_handler.handle_message(user, user_message, character_name)
            # Save character response to database
            message_handler.db_client.append_message(user.id, "assistant", response)
            # Mostrar resposta
            print(f"{character_name}: {response}")
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
            import traceback
            traceback.print_exc()

def create_user_manually(db_client):
    """Manually create a new user."""
    print("\n👤 CREATE NEW USER")
    print("=" * 30)
    
    phone_number = input("Enter phone number: ").strip()
    if not phone_number:
        print("❌ Phone number is required!")
        return
    
    try:
        user = db_client.create_user(phone_number)
        print(f"✅ User created successfully!")
        print(f"   ID: {user.id}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Created: {user.created_at}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")

def list_users(db_client):
    """List all users in the database."""
    print("\n👥 EXISTING USERS")
    print("=" * 30)
    
    try:
        users = db_client.get_active_users()
        if not users:
            print("No users found.")
            return
        
        for user in users:
            print(f"ID: {user.id} | Phone: {user.phone_number} | Active: {user.is_active}")
            if user.current_character:
                print(f"  Current Character: {user.current_character}")
            if user.last_message_time:
                print(f"  Last Message: {user.last_message_time}")
            print()
    except Exception as e:
        print(f"❌ Error listing users: {e}")

def show_conversation_history(db_client):
    """Show conversation history for a user."""
    print("\n📜 CONVERSATION HISTORY")
    print("=" * 30)
    
    phone_number = input("Enter phone number: ").strip()
    if not phone_number:
        print("❌ Phone number is required!")
        return
    
    try:
        user = db_client.get_user_by_phone(phone_number)
        if not user:
            print("❌ User not found!")
            return
        
        limit = input("Number of messages to show (default 10): ").strip()
        limit = int(limit) if limit.isdigit() else 10
        
        messages = db_client.get_recent_messages(user.id, limit)
        
        print(f"\nConversation history for {user.phone_number} (last {len(messages)} messages):")
        print("=" * 60)
        
        for msg in messages:
            timestamp = msg.created_at.strftime("%H:%M:%S") if msg.created_at else "N/A"
            role_emoji = "👤" if msg.role == "user" else "🎭"
            print(f"[{timestamp}] {role_emoji} {msg.content}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error getting conversation history: {e}")

def show_stats(db_client):
    """Show database statistics."""
    print("\n📊 DATABASE STATISTICS")
    print("=" * 30)
    
    try:
        stats = db_client.get_local_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

def reset_data(db_client):
    """Reset all local data."""
    print("\n🗑️ RESET ALL DATA")
    print("=" * 30)
    
    confirm = input("Are you sure you want to reset all data? (y/N): ").strip().lower()
    if confirm == 'y':
        try:
            db_client.reset_local_data()
            print("✅ All data has been reset!")
        except Exception as e:
            print(f"❌ Error resetting data: {e}")
    else:
        print("❌ Reset cancelled.")

if __name__ == "__main__":
    main()
