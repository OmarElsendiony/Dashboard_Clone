import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateTicketComment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        sender_id: str,
        message: str,
        is_public: Optional[bool] = True,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not ticket_id:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: 'ticket_id' is required."
            })

        if not sender_id:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: 'sender_id' is required."
            })

        if not message:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: 'message' is required."
            })

        ticket_id = str(ticket_id).strip()
        sender_id = str(sender_id).strip()
        message = str(message).strip()

        if is_public is not None and not isinstance(is_public, bool):
            val_str = str(is_public).strip().lower()
            if val_str in ['true', '1']:
                is_public = True
            elif val_str in ['false', '0']:
                is_public = False
            else:
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: 'is_public' must be a boolean."
                })
        elif is_public is None:
            is_public = True

        tickets = data.get("tickets", {})
        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        users = data.get("users", {})
        if not isinstance(users, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'users' must be a dictionary"
            })

        ticket_comments = data.get("ticket_comments", {})
        if not isinstance(ticket_comments, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'ticket_comments' must be a dictionary"
            })

        target_ticket = None
        for k, v in tickets.items():
            if isinstance(v, dict) and str(v.get("ticket_id", "")).strip() == ticket_id:
                target_ticket = v
                break

        if not target_ticket:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: ticket_id '{ticket_id}' not found."
            })

        current_status = str(target_ticket.get("status", "")).lower()
        if current_status in ["archived", "deleted", "closed", "resolved"]:
            return json.dumps({
                "success": False,
                "error": "Policy Violation",
                "message": f"Cannot add a comment to a ticket with status '{current_status}'. Ticket must be active/open."
            })

        user_exists = False
        for k, v in users.items():
            if isinstance(v, dict) and str(v.get("user_id", "")).strip() == sender_id:
                user_exists = True
                break

        if not user_exists:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: sender_id '{sender_id}' not found."
            })

        for v in ticket_comments.values():
            if isinstance(v, dict):
                if (str(v.get("ticket_id")) == ticket_id and
                    str(v.get("sender_id")) == sender_id and
                    str(v.get("message")).strip() == message):
                    return json.dumps({
                        "success": False,
                        "error": "Duplicate Comment Detected",
                        "message": f"A comment with this exact content already exists for ticket '{ticket_id}' by sender '{sender_id}'."
                    })

        max_id = 0
        for k in ticket_comments.keys():
            try:
                num = int(str(k))
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

        for v in ticket_comments.values():
            if isinstance(v, dict):
                try:
                    num = int(str(v.get("comment_id", "0")))
                    if num > max_id:
                        max_id = num
                except ValueError:
                    continue

        new_comment_id = str(max_id + 1)
        timestamp = "2026-02-02 23:59:00"

        new_comment = {
            "comment_id": new_comment_id,
            "ticket_id": ticket_id,
            "sender_id": sender_id,
            "message": message,
            "is_public": is_public,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        ticket_comments[new_comment_id] = new_comment

        return json.dumps({
            "success": True,
            "comment": new_comment,
            "message": f"Comment '{new_comment_id}' added to ticket '{ticket_id}' successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_ticket_comment",
                "description": (
                    "Appends a new comment to a specified support ticket. The comment can be designated as either public (visible to customers) or an internal note.\n"
                    " Purpose: Facilitates direct communication and documentation on a ticket. It is strictly used to post required operational messages, including requesting additional details for non-actionable tickets, explicitly linking duplicate tickets to their Master Ticket ID, and providing structured AER (Acknowledge, Empathize, Resolve) replies.\n"
                    " When to use: Use this tool to execute policy steps like 'Check Actionable Ticket', 'Identify and Merge Duplicate Tickets', and 'Structure Replies'.\n"
                    " Returns: Returns a JSON string containing a success boolean, the newly created comment dictionary object, and a success message. Fails if the ticket is in a terminal state (archived, deleted, closed, or resolved) or if an identical comment already exists."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket to add the comment to."
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The unique user identifier of the agent or individual authoring the comment."
                        },
                        "message": {
                            "type": "string",
                            "description": "The text content of the comment or reply."
                        },
                        "is_public": {
                            "type": "boolean",
                            "description": "Set to true if the message should be visible to the customer, or false to save it as a private internal note. Defaults to true."
                        }
                    },
                    "required": ["ticket_id", "sender_id", "message"]
                }
            }
        }
