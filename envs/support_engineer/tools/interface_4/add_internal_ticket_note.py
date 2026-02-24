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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": "Wrong data format",
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": "Wrong data format",
            })

        if ticket_id is None or (isinstance(ticket_id, str) and not ticket_id.strip()):
            return json.dumps({
                "success": bool(False),
                "error": "ticket_id is required",
            })
        if author_id is None or (isinstance(author_id, str) and not author_id.strip()):
            return json.dumps({
                "success": bool(False),
                "error": "author_id is required",
            })
        if body is None or (isinstance(body, str) and not body.strip()):
            return json.dumps({
                "success": bool(False),
                "error": "body is required",
            })

        ticket_id = str(ticket_id)
        author_id = str(author_id)
        body = str(body)
        title = str(title) if title is not None else None

        tickets = data.get("tickets", {})
        users = data.get("users", {})
        ticket_notes = data.get("ticket_notes", {})

        if ticket_id not in tickets:
            return json.dumps({
                "success": bool(False),
                "error": f"Ticket with id '{ticket_id}' not found",
            })

        if author_id not in users:
            return json.dumps({
                "success": bool(False),
                "error": f"User with id '{author_id}' not found",
            })

        if ticket_notes:
            max_id = max(int(k) for k in ticket_notes.keys())
            new_note_id = max_id + 1
        else:
            new_note_id = 1

        static_timestamp = "2026-02-02 23:59:00"

        new_note = {
            "note_id": int(new_note_id),
            "ticket_id": str(ticket_id),
            "author_id": str(author_id),
            "title": str(title) if title is not None else None,
            "body": str(body),
            "is_internal": bool(True),
            "created_at": str(static_timestamp),
        }

        ticket_notes[str(new_note_id)] = new_note

        return json.dumps({
            "success": bool(True),
            "note": new_note,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_internal_ticket_note",
                "description": "Adds an internal note to a ticket (not visible to the customer).",
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
                            "description": "Note title. Defaults to None if omitted.",
                        },
                    },
                    "required": ["ticket_id", "author_id", "body"],
                },
            },
        }
