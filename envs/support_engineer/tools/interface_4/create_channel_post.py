import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateChannelPost(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        sender_id: str,
        message: str,
        related_ticket_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not channel_id:
            return json.dumps({"success": False, "error": "channel_id is required"})

        if not sender_id:
            return json.dumps({"success": False, "error": "sender_id is required"})

        if not message:
            return json.dumps({"success": False, "error": "message is required"})

        channels = data.get("channels", {})
        users = data.get("users", {})
        tickets = data.get("tickets", {})
        channel_messages = data.get("channel_messages", {})

        if str(channel_id) not in channels:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Channel with id '{channel_id}' not found",
                }
            )

        if str(sender_id) not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with id '{sender_id}' not found",
                }
            )

        sender = users[str(sender_id)]
        if sender.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Sender availability must be 'active'. Current status: '{sender.get('status', 'unknown')}'",
                }
            )

        if related_ticket_id is not None:
            if str(related_ticket_id) not in tickets:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with id '{related_ticket_id}' not found",
                    }
                )

        if channel_messages:
            max_id = max(int(k) for k in channel_messages.keys())
            new_message_id = str(max_id + 1)
        else:
            new_message_id = "1"

        static_timestamp = "2026-02-02 23:59:00"

        new_message = {
            "message_id": new_message_id,
            "channel_id": channel_id,
            "sender_id": sender_id,
            "message": message,
            "related_ticket_id": related_ticket_id,
            "sent_at": static_timestamp,
            "created_at": static_timestamp,
            "updated_at": static_timestamp,
        }

        channel_messages[new_message_id] = new_message

        return json.dumps({"success": True, "message": new_message})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_channel_post",
                "description": "Post a message to a communication channel for internal team collaboration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Channel identifier to post message to",
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "User identifier sending the message",
                        },
                        "message": {
                            "type": "string",
                            "description": "Message content to post",
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this message relates to",
                        },
                    },
                    "required": ["channel_id", "sender_id", "message"],
                },
            },
        }
