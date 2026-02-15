import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class PostChannelMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_name: str,
        sender_email: str,
        message: str,
        ticket_number: str,
    ) -> str:
        if not channel_name:
            return json.dumps({"error": "channel_name is required"})

        if not sender_email:
            return json.dumps({"error": "sender_email is required"})

        if not message:
            return json.dumps({"error": "message is required"})

        if not ticket_number:
            return json.dumps({"error": "ticket_number is required"})

        channels = data.get("channels", {})
        users = data.get("users", {})
        tickets = data.get("tickets", {})
        channel_messages = data.get("channel_messages", {})
        timestamp = "2026-02-02 23:59:00"

        channel_id = None
        for c_id, channel in channels.items():
            if channel.get("name") == str(channel_name):
                channel_id = c_id
                break

        if not channel_id:
            return json.dumps({"error": f"Channel with name '{channel_name}' not found"})

        sender_id = None
        for u_id, user in users.items():
            if user.get("email") == str(sender_email) and user.get("status") == "active":
                sender_id = u_id
                break

        if not sender_id:
            return json.dumps({"error": f"Active user with email '{sender_email}' not found"})

        related_ticket_id = None
        for t_id, ticket in tickets.items():
            if ticket.get("ticket_number") == ticket_number:
                related_ticket_id = t_id
                break

        if not related_ticket_id:
            return json.dumps({"error": f"Ticket with number '{ticket_number}' not found"})

        if not channel_messages:
            message_id = "1"
        else:
            message_id = str(max(int(k) for k in channel_messages.keys()) + 1)

        new_message = {
            "message_id": str(message_id),
            "channel_id": str(channel_id),
            "thread_id": None,
            "sender_id": str(sender_id),
            "message": str(message),
            "related_ticket_id": str(related_ticket_id),
            "sent_at": timestamp,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        channel_messages[message_id] = new_message

        return json.dumps({
            "success": True,
            "channel_message": {
                "message_id": str(new_message["message_id"]),
                "channel_id": str(new_message["channel_id"]),
                "channel_name": str(channel_name),
                "sender_id": str(new_message["sender_id"]),
                "sender_email": str(sender_email),
                "message": str(new_message["message"]),
                "related_ticket_id": str(new_message["related_ticket_id"]),
                "ticket_number": str(ticket_number),
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
                "name": "post_channel_message",
                "description": "Posts a message to a specified channel for internal alignment during ticket resolution. It links the message to an existing ticket. It should be used when you want to communicate important information related to a ticket within the team channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_name": {
                            "type": "string",
                            "description": "The name of the channel",
                        },
                        "sender_email": {
                            "type": "string",
                            "description": "The email of the message sender",
                        },
                        "message": {
                            "type": "string",
                            "description": "The message content",
                        },
                        "ticket_number": {
                            "type": "string",
                            "description": "The ticket number to link to the message",
                        },
                    },
                    "required": ["channel_name", "sender_email", "message", "ticket_number"],
                },
            },
        }
