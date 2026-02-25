import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class PostMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        message_body: str,
        sender_id: str
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        channels = data.get("channels", {})
        messages = data.get("messages", {})
        users = data.get("users", {})
        
        # Validate required fields
        if not all([channel_id, message_body, sender_id]):
            return json.dumps({
                "success": False,
                "error": "Missing required parameters: channel_id, message_body, and sender_id are required"
            })
        
        # Validate channel exists
        if str(channel_id) not in channels:
            return json.dumps({
                "success": False,
                "error": f"Channel with ID '{channel_id}' not found"
            })
        
        # Validate channel is active
        channel = channels[str(channel_id)]
        if channel.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"Channel '{channel_id}' is not active"
            })
        
        # Validate sender exists
        if str(sender_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Sender with user_id '{sender_id}' not found"
            })
        
        # Generate new message ID
        new_message_id = generate_id(messages)
        
        # Create new message record - Strictly matching DB schema (including None for thread_id)
        new_message = {
            "message_id": str(new_message_id),
            "channel_id": str(channel_id),
            "thread_id": None,
            "sender_id": str(sender_id),
            "message_body": str(message_body),
            "sent_at": "2026-02-11T23:59:00"
        }
        
        # Add to messages data
        messages[str(new_message_id)] = new_message
        
        # Explicitly build response data
        message_data = {
            "message_id": str(new_message_id),
            "channel_id": str(channel_id),
            "thread_id": None,
            "sender_id": str(sender_id),
            "message_body": str(message_body),
            "sent_at": "2026-02-11T23:59:00"
        }
        
        return json.dumps({
            "success": True,
            "message": "Message posted successfully",
            "message_id": str(new_message_id),
            "message_data": message_data
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "post_message",
                "description": "Posts a message to a communication channel. Use this to send status updates, notify stakeholders, escalate issues, communicate program information to teams, or announce decisions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The ID of the channel to post to (required, must exist and be active)"
                        },
                        "message_body": {
                            "type": "string",
                            "description": "The message content (required)"
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The ID of the user sending the message (required, must exist)"
                        }
                    },
                    "required": ["channel_id", "message_body", "sender_id"]
                }
            }
        }
