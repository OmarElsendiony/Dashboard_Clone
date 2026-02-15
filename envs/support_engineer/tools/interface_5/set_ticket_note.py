from typing import Dict, Optional
import json
from tau_bench.envs.tool import Tool

class SetTicketNote(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        ticket_id: str,
        body: str,
        author_id: str,
        title: Optional[str] = None,
        file_path: Optional[str] = None,
        is_high_risk: bool = False,
    ) -> str:
        tickets = data.get("tickets", {})
        ticket_notes = data.get("ticket_notes", {})
        users = data.get("users", {})

        if not ticket_id:
            return json.dumps({"error": "ticket_id is required"})

        if not body:
            return json.dumps({"error": "body is required"})

        if not author_id:
            return json.dumps({"error": "author_id is required"})

        ticket = tickets.get(ticket_id)
        if not ticket:
            return json.dumps({"error": f"Ticket with ID {ticket_id} not found"})

        author = users.get(author_id)
        if not author:
            return json.dumps({"error": f"User with ID {author_id} not found"})

        timestamp = "2026-02-02 23:59:00"
        if not ticket_notes:
            note_id = "1"
        else:
            note_id = str(max(int(k) for k in ticket_notes.keys()) + 1)

        new_note = {
            "note_id": str(note_id),
            "ticket_id": str(ticket_id),
            "author_id": str(author_id),
            "title": str(title) if title else None,
            "body": str(body),
            "file_path": str(file_path) if file_path else None,
            "is_high_risk": bool(is_high_risk),
            "sanitization_status": "Clean",
            "created_at": timestamp,
        }

        ticket_notes[note_id] = new_note

        return json.dumps({"success": True, "note_id": note_id, "note": new_note})

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "set_ticket_note",
                "description": "Add an internal note to a ticket with title, body, author information, file path reference, and risk classification. Use this to document triage decisions, deduplication findings, technical ownership mapping, branch creation, PR status updates, or any other internal information that should be recorded on the ticket. ticket_id, body, and author_id are required.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Unique identifier of the ticket to add a note to",
                        },
                        "body": {
                            "type": "string",
                            "description": "Content of the note",
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional title for the note",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "ID of the user creating the note (required)",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Optional file path if the note references an attachment",
                        },
                        "is_high_risk": {
                            "type": "boolean",
                            "description": "Whether this note contains high-risk information",
                        },
                    },
                    "required": ["ticket_id", "body", "author_id"],
                },
            },
        }
