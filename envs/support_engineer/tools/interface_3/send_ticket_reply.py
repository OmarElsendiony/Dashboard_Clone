import json
from typing import Dict, Any
from tau_bench.envs.tool import Tool


class SendTicketReply(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_number: str,
        message: str,
        sender_email: str,
    ) -> str:
        if not ticket_number:
            return json.dumps({"error": "ticket_number is required"})

        if not message:
            return json.dumps({"error": "message is required"})

        if not sender_email:
            return json.dumps({"error": "sender_email is required"})

        tickets = data.get("tickets", {})
        ticket_comments = data.get("ticket_comments", {})
        users = data.get("users", {})
        timestamp = "2026-02-02 23:59:00"

        ticket_id = None
        ticket_details = None

        for t_id, t_details in tickets.items():
            if t_details.get("ticket_number") == ticket_number:
                ticket_id = t_id
                ticket_details = t_details
                break

        if not ticket_details:
            return json.dumps({"error": f"Ticket with number '{ticket_number}' not found"})

        user_details = None
        user_id = None

        for u_id, user in users.items():
            if user.get("email") == str(sender_email) and user.get("role") == "support_engineer" and user.get("status") == "active":
                user_details = user
                user_id = u_id
                break

        if not user_details:
            return json.dumps({"error": f"No active support engineer found with email '{sender_email}'"})

        if not ticket_comments:
            comment_id = "1"
        else:
            comment_id = str(max(int(k) for k in ticket_comments.keys()) + 1)

        new_reply = {
            "comment_id": comment_id,
            "ticket_id": str(ticket_id),
            "sender_id": str(user_id),
            "message": str(message),
            "is_public": True,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        ticket_comments[comment_id] = new_reply

        return json.dumps({
            "success": True,
            "reply": {
                "comment_id": str(new_reply["comment_id"]),
                "ticket_id": str(new_reply["ticket_id"]),
                "ticket_number": str(ticket_details["ticket_number"]),
                "sender_id": str(new_reply["sender_id"]),
                "sender_email": str(user_details["email"]),
                "message": str(new_reply["message"]),
                "created_at": str(new_reply["created_at"]),
                "updated_at": str(new_reply["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_ticket_reply",
                "description": "Sends a reply to an existing ticket in the ticketing system. It should be used when you need to respond to a ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_number": {
                            "type": "string",
                            "description": "The number of the ticket",
                        },
                        "message": {
                            "type": "string",
                            "description": "The message to send as a reply",
                        },
                        "sender_email": {
                            "type": "string",
                            "description": "The email of the sender",
                        },
                    },
                    "required": ["ticket_number", "message", "sender_email"],
                },
            },
        }
