import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddTicketComment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        sender_id: str,
        message: str,
        is_public: bool = True,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not ticket_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'ticket_id'"})

        if not sender_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'sender_id'"})

        if not message:
            return json.dumps({"success": False, "error": "Missing required parameter: 'message'"})

        tickets_dict = data.get("tickets", {})
        ticket_comments_dict = data.get("ticket_comments", {})
        users_dict = data.get("users", {})

        # Convert and validate inputs
        ticket_id_str = str(ticket_id).strip()
        sender_id_str = str(sender_id).strip()
        message_str = str(message).strip()

        if not isinstance(is_public, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid input value for is_public. Expected True or False"
            })

        if ticket_id_str not in tickets_dict:
            return json.dumps({
                "success": False,
                "error": f"Ticket with ID '{ticket_id_str}' not found"
            })

        ticket = tickets_dict[ticket_id_str]

        if not isinstance(ticket, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid ticket data structure for ticket ID '{ticket_id_str}'"
            })

        if sender_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{sender_id_str}' not found"
            })

        sender = users_dict[sender_id_str]

        if not isinstance(sender, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid user data structure for sender ID '{sender_id_str}'"
            })

        if not message_str:
            return json.dumps({
                "success": False,
                "error": "Comment message cannot be empty"
            })

        # Check ticket status - cannot add comments to deleted or archived tickets
        ticket_status = str(ticket.get("status", "")).strip()

        invalid_statuses = ["deleted", "archived"]
        if ticket_status in invalid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Cannot add comment to ticket '{ticket_id_str}' with status '{ticket_status}'"
            })

        # Create new comment
        new_comment_id = generate_id(ticket_comments_dict)
        new_comment = {
            "comment_id": str(new_comment_id) if new_comment_id else None,
            "ticket_id": str(ticket_id_str) if ticket_id_str else None,
            "sender_id": str(sender_id_str) if sender_id_str else None,
            "message": str(message_str) if message_str else None,
            "is_public": is_public,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add comment to dictionary
        ticket_comments_dict[new_comment_id] = new_comment

        # Prepare return data
        comment_return = new_comment.copy()
        comment_return["sender_email"] = str(sender.get("email", "")).strip()
        comment_return["sender_name"] = str(f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip())
        comment_return["ticket_number"] = str(ticket.get("ticket_number"))

        # Build success message
        visibility = "public" if is_public else "internal"
        message_text = f"{visibility.capitalize()} comment added successfully to ticket '{ticket.get('ticket_number', ticket_id_str)}'"

        return json.dumps({
            "success": True,
            "comment": comment_return,
            "message": message_text,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_ticket_comment",
                "description": (
                    "Adds a comment to an existing ticket. "
                    "This function creates a new comment entry associated with a ticket, "
                    "which can be either public (visible to customers) or internal (visible only to support staff). "
                    "Use this to request missing details for a ticket."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket to add the comment to.",
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The unique identifier of the user adding the comment.",
                        },
                        "message": {
                            "type": "string",
                            "description": "The content of the comment to add to the ticket.",
                        },
                        "is_public": {
                            "type": "boolean",
                            "description": "Whether the comment is public (visible to customers) or internal (visible only to support staff). Default is True (public).",
                        },
                    },
                    "required": ["ticket_id", "sender_id", "message"],
                },
            },
        }
