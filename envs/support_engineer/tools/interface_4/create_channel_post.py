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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        channel_id_str = str(channel_id).strip() if channel_id is not None else ""
        if not channel_id_str:
            return json.dumps({
                "success": bool(False),
                "error": str("channel_id is required"),
            })

        sender_id_str = str(sender_id).strip() if sender_id is not None else ""
        if not sender_id_str:
            return json.dumps({
                "success": bool(False),
                "error": str("sender_id is required"),
            })

        if message is None:
            return json.dumps({
                "success": bool(False),
                "error": str("message is required"),
            })
        message = str(message).strip()
        if not message:
            return json.dumps({
                "success": bool(False),
                "error": str("message is required"),
            })

        channels = data.get("channels", {})
        users = data.get("users", {})
        tickets = data.get("tickets", {})
        channel_messages = data.get("channel_messages", {})

        if channel_id_str not in channels:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Channel with id '{channel_id_str}' not found"),
            })

        if sender_id_str not in users:
            return json.dumps({
                "success": bool(False),
                "error": str(f"User with id '{sender_id_str}' not found"),
            })

        sender = users[sender_id_str]
        if sender.get("status") != "active":
            return json.dumps({
                "success": bool(False),
                "error": str(
                    f"Sender availability must be 'active'. Current status: '{sender.get('status', 'unknown')}'"
                ),
            })

        if related_ticket_id is not None:
            if str(related_ticket_id) not in tickets:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Ticket with id '{related_ticket_id}' not found"),
                })

        if channel_messages:
            max_id = max(int(k) for k in channel_messages.keys())
            new_message_id = str(max_id + 1)
        else:
            new_message_id = str("1")

        static_timestamp = str("2026-02-02 23:59:00")

        new_message = {
            "message_id": str(new_message_id),
            "channel_id": str(channel_id_str),
            "sender_id": str(sender_id_str),
            "message": str(message),
            "related_ticket_id": str(related_ticket_id) if related_ticket_id is not None else None,
            "sent_at": str(static_timestamp),
            "created_at": str(static_timestamp),
            "updated_at": str(static_timestamp),
        }

        channel_messages[new_message_id] = new_message

        return json.dumps({
            "success": bool(True),
            "message": {
                "message_id": str(new_message["message_id"]),
                "channel_id": str(new_message["channel_id"]),
                "sender_id": str(new_message["sender_id"]),
                "message": str(new_message["message"]),
                "related_ticket_id": str(new_message["related_ticket_id"]) if new_message["related_ticket_id"] is not None else None,
                "sent_at": str(new_message["sent_at"]),
                "created_at": str(new_message["created_at"]),
                "updated_at": str(new_message["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_channel_post",
                "description": "Posts a message to a communication channel for internal team collaboration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Channel identifier to post the message to.",
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "User identifier sending the message.",
                        },
                        "message": {
                            "type": "string",
                            "description": "Message content to post.",
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this message relates to.",
                        },
                    },
                    "required": ["channel_id", "sender_id", "message"],
                },
            },
        }
