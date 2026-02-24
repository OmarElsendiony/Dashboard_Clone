import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SanitizeAttachment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        note_id: str,
        ticket_id: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        ticket_notes = data.get("ticket_notes", {})

        if not note_id:
             return json.dumps({"success": False, "error": "Missing Argument: 'note_id' is required."})

        target_note = None

        if str(note_id) in ticket_notes:
            target_note = ticket_notes[str(note_id)]

        if not target_note:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: Note ID '{note_id}' not found."
            })

        if ticket_id:
            if str(target_note.get("ticket_id")) != str(ticket_id):
                return json.dumps({
                    "success": False,
                    "error": f"Integrity Error: Note '{note_id}' does not belong to Ticket '{ticket_id}'."
                })

        current_file = target_note.get("file_path")
        if not current_file:
            return json.dumps({
                "success": False,
                "error": "Action Failed: No file attachment found on this note to sanitize."
            })

        target_note["file_path"] = None
        target_note["sanitization_status"] = "Purged"
        target_note["is_high_risk"] = True
        target_note["updated_at"] = "2026-02-02 23:59:00"

        note_return = target_note.copy()
        note_return["note_id"] = str(note_id)
        note_return["ticket_id"] = str(target_note.get("ticket_id", ""))
        note_return["file_path"] = str(target_note.get("file_path"))
        note_return["sanitization_status"] = str(target_note.get("sanitization_status"))
        note_return["is_high_risk"] = bool(target_note.get("is_high_risk"))
        note_return["updated_at"] = str(target_note.get("updated_at"))
        note_return["previous_file"] = str(current_file)
        note_return["success"] = bool(True)
        note_return["status"] = str("Purged")
        note_return["message"] = str(f"Attachment '{current_file}' has been permanently purged from Note {note_id}.")

        return json.dumps(note_return)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "sanitize_attachment",
                "description": (
                    "A security compliance tool that performs a hard delete of specific file objects. "
                    " Purpose: Removes dangerous files (e.g., .pem, .key, .p12, .env) detected during ticket ingestion or review, while leaving the conversational text intact. "
                    " When to use: Immediately upon identifying a high-risk file attachment in a ticket note, if it is needed to sanitize sensitive data. "
                    " Returns: JSON confirmation of the purge action."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "note_id": {
                            "type": "string",
                            "description": "REQUIRED. The unique identifier of the ticket note containing the attachment."
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "OPTIONAL. The Ticket ID for validation, ensuring the note belongs to the expected record."
                        }
                    },
                    "required": ["note_id"]
                }
            }
        }
