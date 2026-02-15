import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class SetTicketReply(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        message: str,
        sender_id: str,
        is_public: bool = True,
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)

        if not ticket_id:
            return json.dumps({"success": False, "error": "Ticket ID is required"})

        if not message:
            return json.dumps({"success": False, "error": "Message content is required"})

        if not sender_id:
            return json.dumps({"success": False, "error": "Sender ID is required"})

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )
        tickets = data.get("tickets", {})
        # Validate ticket existence
        if not ticket_id or ticket_id not in tickets:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket with ID '{ticket_id}' does not exist",
                }
            )
        ticket = tickets[ticket_id]
        if not message:
            return json.dumps(
                {
                    "success": False,
                    "error": "Message cannot be empty",
                }
            )
        if not sender_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Sender ID cannot be empty",
                }
            )
        # validate the sender exists
        users = data.get("users", {})
        if sender_id not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Sender with ID '{sender_id}' does not exist",
                }
            )
        truthy_values = [True, "true", "True", "1", 1]
        # Append reply to ticket comments
        comments = data.get("ticket_comments", {})
        new_comment = {
            "comment_id": generate_id(comments),
            "ticket_id": str(ticket_id),
            "sender_id": str(sender_id),
            "message": str(message),
            "is_public": bool(is_public in truthy_values),
            "created_at": "2026-02-02 23:59:00",
            "updated_at": "2026-02-02 23:59:00",
        }
        comments[new_comment["comment_id"]] = new_comment
        tickets[ticket_id] = ticket
        return json.dumps(
            {
                "success": True,
                "ticket": ticket,
                "new_comment": new_comment,
            }
        )


    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_ticket_reply",
                "description": "Adds a new comment to an existing support ticket. This tool allows for both public communication with the customer and for team collaboration, depending on the visibility flag. Use this to provide updates or request more information on a specific case.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The ID of the ticket to update.",
                        },
                        "message": {
                            "type": "string",
                            "description": "The reply message to add to the ticket.",
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The ID of the sender of the reply.",
                        },
                        "is_public": {
                            "type": "boolean",
                            "description": "Indicates if the reply is public or internal.",
                            "default": True,
                        },
                    },
                    "required": ["ticket_id", "message", "sender_id"],
                },
            },
        }
