import json
from typing import Dict, Optional, Any  
from tau_bench.envs.tool import Tool


class FetchTicketReplies(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_number: str,
        sender_email: Optional[str] = None,
    ) -> str:
        if not ticket_number:
            return json.dumps({"error": "ticket_number is required"})

        tickets = data.get("tickets", {})
        ticket_comments = data.get("ticket_comments", {})
        users = data.get("users", {})

        ticket_id = None
        for t_id, t_details in tickets.items():
            if t_details.get("ticket_number") == ticket_number:
                ticket_id = t_id
                break

        if not ticket_id:
            return json.dumps({"error": f"Ticket with number '{ticket_number}' not found"})

        sender_id = None
        if sender_email:
            for u_id, user in users.items():
                if user.get("email") == str(sender_email):
                    sender_id = u_id
                    break

            if not sender_id:
                return json.dumps({"error": f"User with email '{sender_email}' not found"})

        replies = []
        for comment in ticket_comments.values():
            if str(comment.get("ticket_id")) != str(ticket_id):
                continue

            if sender_id and str(comment.get("sender_id")) != str(sender_id):
                continue

            replies.append({
                "comment_id": str(comment["comment_id"]),
                "ticket_id": str(comment["ticket_id"]),
                "sender_id": str(comment["sender_id"]),
                "message": str(comment["message"]),
                "created_at": str(comment["created_at"]),
                "updated_at": str(comment["updated_at"]),
            })

        replies.sort(key=lambda r: r.get("created_at", ""))

        return json.dumps({
            "success": True,
            "ticket_number": str(ticket_number),
            "total_replies": len(replies),
            "replies": replies,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_ticket_replies",
                "description": "Fetches replies for a ticket from the ticketing system. It should be used when you need to retrieve replies associated with a specific ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_number": {
                            "type": "string",
                            "description": "The number of the ticket",
                        },
                        "sender_email": {
                            "type": "string",
                            "description": "The email of the sender to filter replies by",
                        },
                    },
                    "required": ["ticket_number"],
                },
            },
        }
