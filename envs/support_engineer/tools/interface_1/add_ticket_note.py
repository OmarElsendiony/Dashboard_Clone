import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddTicketNote(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        author_id: str,
        body: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not all([ticket_id, author_id, body]):
            return json.dumps({"success": False, "error": "Missing required arguments: ticket_id, author_id, and body are all required."})

        ticket_id = str(ticket_id).strip()
        author_id = str(author_id).strip()
        body = str(body).strip()

        tickets = data.get("tickets", {})
        users = data.get("users", {})
        ticket_notes = data.get("ticket_notes", {})

        if not isinstance(tickets, dict) or not isinstance(users, dict) or not isinstance(ticket_notes, dict):
            return json.dumps({"success": False, "error": "Internal data structure error: missing required tables."})

        if ticket_id not in tickets:
            return json.dumps({"success": False, "error": f"Not Found Error: ticket_id '{ticket_id}' not found."})

        target_ticket = tickets[ticket_id]
        current_status = str(target_ticket.get("status", "")).lower()

        if current_status in ["archived", "deleted", "closed", "resolved"]:
            return json.dumps({
                "success": False,
                "error": "Policy Violation",
                "message": f"Cannot add a note to a ticket with status '{current_status}'. Ticket must be active/open."
            })

        if author_id not in users:
            return json.dumps({"success": False, "error": f"Not Found Error: author_id '{author_id}' not found."})

        for note in ticket_notes.values():
            if (str(note.get("ticket_id")) == ticket_id and
                str(note.get("author_id")) == author_id and
                str(note.get("body")).strip() == body):
                return json.dumps({
                    "success": False,
                    "error": "Duplicate Note Detected",
                    "message": f"A note with this exact content already exists for ticket '{ticket_id}' by author '{author_id}'."
                })

        max_id = 0
        for k in ticket_notes.keys():
            try:
                num = int(str(k))
                if num > max_id: max_id = num
            except ValueError: continue

        new_note_id = str(max_id + 1)
        timestamp = "2026-02-02 23:59:00"

        new_note = {
            "note_id": new_note_id,
            "ticket_id": ticket_id,
            "author_id": author_id,
            "body": body,
            "is_internal": True,
            "sanitization_status": "Clean",
            "created_at": timestamp
        }

        ticket_notes[new_note_id] = new_note

        return json.dumps({
            "success": True,
            "note": new_note,
            "message": f"Internal note '{new_note_id}' successfully added."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_ticket_note",
                "description": (
                    "Adds a private entry to the 'ticket_notes' table.\n"
                    " Purpose: Used for the 'Revocation' SOP to flag accounts for Billing review. Includes a safety check to prevent duplicate notes with identical content.\n"
                    " When to use: Use after identifying an 'inactive' or 'suspended' account to provide an internal audit trail.\n"
                    " Returns: Returns the new note. Fails if an identical note already exists for this ticket and author, or if the ticket is in a terminal state (archived, deleted, closed, or resolved)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string", "description": "The target ticket ID."},
                        "author_id": {"type": "string", "description": "The agent creating the note."},
                        "body": {"type": "string", "description": "The text content (e.g., 'Account flagged for review')."}
                    },
                    "required": ["ticket_id", "author_id", "body"]
                }
            }
        }
