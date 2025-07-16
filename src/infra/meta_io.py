import requests
from typing import Optional, Dict, Any
from src.models.user import User
from src.infra.supabase_client import SupabaseClient
from datetime import datetime

class MetaIO:
    """
    Handles communication with Meta's WhatsApp Business API or local terminal output.
    
    This class provides functionality for sending messages and templates through
    the WhatsApp Business API, as well as parsing incoming webhook data. It manages
    authentication, request formatting, and error handling for Meta API interactions.
    In local mode, it prints messages to the terminal instead of sending to Meta.
    
    Attributes:
        local_mode (bool): Whether to use local terminal output instead of Meta API
        access_token (str): Authentication token for regular messages
        template_access_token (str): Authentication token for template messages
        phone_number_id (str): WhatsApp Business phone number identifier
        base_url (str): Base URL for Meta API requests
        db_client (SupabaseClient): Database client for message storage
    """
    
    def __init__(self, access_token: str = None, template_access_token: str = None, 
                 phone_number_id: str = None, db_client: SupabaseClient = None, 
                 local_mode: bool = False):
        """
        Initialize the Meta IO client.
        
        Args:
            access_token (str): Authentication token for regular messages (ignored in local mode)
            template_access_token (str): Authentication token for template messages (ignored in local mode)
            phone_number_id (str): WhatsApp Business phone number identifier (ignored in local mode)
            db_client (SupabaseClient): Database client for message storage
            local_mode (bool): Whether to use local terminal output instead of Meta API
        """
        self.local_mode = local_mode
        self.db_client = db_client
        
        if local_mode:
            self.access_token = None
            self.template_access_token = None
            self.phone_number_id = None
            self.base_url = None
            print("Meta IO client initialized in LOCAL MODE - messages will be printed to terminal")
        else:
            if not access_token or not template_access_token or not phone_number_id:
                raise ValueError("access_token, template_access_token, and phone_number_id are required when not in local mode")
            self.access_token = access_token
            self.template_access_token = template_access_token
            self.phone_number_id = phone_number_id
            self.base_url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
            print("Meta IO client initialized")

    def send_message(self, user: User, message: str) -> bool:
        """
        Send a WhatsApp message to a specific phone number.
        
        In local mode, this method prints the message to the terminal.
        In normal mode, this method:
        1. Formats the message payload according to Meta API requirements
        2. Sets up authentication headers
        3. Makes a POST request to the Meta API
        4. Handles success/failure logging
        5. Returns success status
        
        Args:
            user (User): User object containing the phone number
            message (str): Text message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            to = user.phone_number
            
            if self.local_mode:
                print(f"\n{'='*50}")
                print(f"📱 WHATSAPP MESSAGE (LOCAL MODE)")
                print(f"To: {to}")
                print(f"Message: {message}")
                print(f"{'='*50}\n")
                
                if self.db_client:
                    self.db_client.append_message(user.id, "assistant", message)
                return True
            
            print(f"Sending message to {to}")
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": message}
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            
            print(f"Message sent successfully to {to}")
            if self.db_client:
                self.db_client.append_message(user.id, "assistant", message)
            return True
            
        except Exception as e:
            print(f"Error sending message to {to}: {str(e)}")
            return False

    def send_template_message(self, user: User, template_name: str, dict_params: Dict[str, Any]) -> bool:
        """
        Send a WhatsApp template message to a specific phone number using Meta's Business API.
        
        In local mode, this method prints the template message to the terminal.
        In normal mode, this method handles the complete process of sending a template-based message:
        1. Constructs a properly formatted payload with template parameters
        2. Sets up authentication headers using the template-specific access token
        3. Makes a POST request to the Meta API endpoint
        4. Handles both HTTP-specific and general error cases with detailed logging
        5. Returns a boolean indicating the success/failure of the operation
        
        The template message will be sent in Brazilian Portuguese (pt_BR) by default.
        All parameters in dict_params will be converted to text type parameters in the template.
        
        Args:
            user (User): User object containing the phone number
            template_name (str): Name of the approved template as registered in Meta Business Manager
            dict_params (Dict[str, Any]): Dictionary mapping parameter names to their values.
                Each parameter will be substituted in the template where {parameter_name} appears.
            
        Returns:
            bool: True if the template message was sent successfully, False if any error occurred
                during the process. All errors are logged with appropriate detail.
        """
        try:
            to = user.phone_number
            
            if self.local_mode:
                print(f"\n{'='*50}")
                print(f"📱 WHATSAPP TEMPLATE MESSAGE (LOCAL MODE)")
                print(f"To: {to}")
                print(f"Template: {template_name}")
                print(f"Parameters: {dict_params}")
                print(f"{'='*50}\n")
                return True
            
            print(f"Sending template message '{template_name}' to {to}")
            
            headers = {
                "Authorization": f"Bearer {self.template_access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "pt_BR"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "parameter_name": param_name,
                                    "text": param_value
                                } for param_name, param_value in dict_params.items()
                            ]
                        }
                    ]
                }
            }

            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            
            print(f"Template message '{template_name}' sent successfully to {to}")
            return True
            
        except requests.exceptions.HTTPError as e:
            # Log template-specific errors for debugging
            error_detail = ""
            try:
                error_detail = response.json()
            except:
                error_detail = response.text
            print(f"HTTP error sending template to {to}: {e}. Response: {error_detail}")
            return False
            
        except Exception as e:
            print(f"Error sending template message to {to}: {str(e)}")
            return False

    def parse_webhook(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming webhook data from Meta.
        
        This method:
        1. Validates the webhook data structure
        2. Extracts message details from nested JSON
        3. Handles various error cases
        4. Returns formatted message data
        
        The method checks for:
        - Presence of entries
        - Presence of changes
        - Presence of messages
        - Required message fields
        
        Args:
            webhook_data (Dict[str, Any]): Raw webhook data from Meta
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing:
                - from: Sender's phone number
                - message: Message text
                - timestamp: Message timestamp
                None if parsing fails
        """
        try:
            print(f"Parsing webhook data: {webhook_data}")
            
            if not webhook_data.get('entry'):
                print("No entries in webhook data")
                return None
                
            entry = webhook_data['entry'][0]
            if not entry.get('changes'):
                print("No changes in webhook entry")
                return None
                
            change = entry['changes'][0]
            if not change.get('value', {}).get('messages'):
                print("No messages in webhook change")
                return None
                
            message = change['value']['messages'][0]
            
            if 'from' not in message or 'text' not in message:
                print("Invalid message format in webhook")
                return None
                
            result = {
                'from': message.get('from'),
                'message': message.get('text', {}).get('body', ''),
                'timestamp': message.get('timestamp')
            }
            
            print(f"Successfully parsed webhook data for {result['from']}")
            return result
            
        except Exception as e:
            print(f"Error parsing webhook: {str(e)}")
            return None

    def simulate_incoming_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Simulate an incoming message for local mode testing.
        
        This method creates a mock webhook data structure that mimics
        what would come from Meta's webhook, allowing you to test
        message processing in local mode.
        
        Args:
            phone_number (str): The phone number sending the message
            message (str): The message content
            
        Returns:
            Dict[str, Any]: Mock webhook data structure
        """
        if not self.local_mode:
            raise ValueError("simulate_incoming_message() is only available in local mode")
        
        mock_webhook = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": phone_number,
                                        "text": {
                                            "body": message
                                        },
                                        "timestamp": str(int(datetime.now().timestamp()))
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        print(f"\n{'='*50}")
        print(f"📥 SIMULATED INCOMING MESSAGE (LOCAL MODE)")
        print(f"From: {phone_number}")
        print(f"Message: {message}")
        print(f"{'='*50}\n")
        
        return mock_webhook