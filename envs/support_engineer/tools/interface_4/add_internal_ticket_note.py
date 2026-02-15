import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddInternalTicketNote(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        author_id: str,
        body: str,
        title: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not ticket_id:
            return json.dumps({"success": False, "error": "ticket_id is required"})

        if not author_id:
            return json.dumps({"success": False, "error": "author_id is required"})

        if not body:
            return json.dumps({"success": False, "error": "body is required"})

        tickets = data.get("tickets", {})
        users = data.get("users", {})
        ticket_notes = data.get("ticket_notes", {})

        if str(ticket_id) not in tickets:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket with id '{ticket_id}' not found",
                }
            )

        if str(author_id) not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with id '{author_id}' not found",
                }
            )

        if ticket_notes:
            max_id = max(int(k) for k in ticket_notes.keys())
            new_note_id = max_id + 1
        else:
            new_note_id = 1

        static_timestamp = "2026-02-02 23:59:00"

        new_note = {
            "note_id": new_note_id,
            "ticket_id": ticket_id,
            "author_id": author_id,
            "title": title,
            "body": body,
            "is_internal": True,
            "created_at": static_timestamp,
        }

        ticket_notes[str(new_note_id)] = new_note

        return json.dumps({"success": True, "note": new_note})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_internal_ticket_note",
                "description": "Add an internal note to a ticket (not visible to the customer).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier to add the note to",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "User identifier of the note author",
                        },
                        "body": {
                            "type": "string",
                            "description": "Note content",
                        },
                        "title": {
                            "type": "string",
                            "description": "Note title",
                        },
                    },
                    "required": ["ticket_id", "author_id", "body"],
                },
            },
        }
