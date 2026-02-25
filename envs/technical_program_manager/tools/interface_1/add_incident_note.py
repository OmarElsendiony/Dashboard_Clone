import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddIncidentNote(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: str,
        author_id: str,
        note_text: str
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        incidents = data.get("incidents", {})
        users = data.get("users", {})
        incident_notes = data.get("incident_notes", {})
        
        if not incident_id or not author_id or not note_text:
            return json.dumps({
                "success": False,
                "error": "Missing parameters: incident_id, author_id, and note_text"
            })
            
        if str(incident_id) not in incidents:
            return json.dumps({
                "success": False,
                "error": f"Incident with ID '{incident_id}' not found"
            })
            
        if str(author_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Author with user_id '{author_id}' not found"
            })
            
        new_note_id = generate_id(incident_notes)
        
        new_note = {
            "note_id": str(new_note_id),
            "incident_id": str(incident_id),
            "author_id": str(author_id),
            "note_text": str(note_text),
            "created_at": "2026-02-11T23:59:00"
        }
        
        incident_notes[str(new_note_id)] = new_note
        
        note_response = {
            "note_id": str(new_note_id),
            "incident_id": str(incident_id),
            "author_id": str(author_id),
            "note_text": str(note_text),
            "created_at": "2026-02-11T23:59:00"
        }
        
        return json.dumps({
            "success": True,
            "message": "Incident note added successfully",
            "note_data": note_response
        })
        
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_incident_note",
                "description": "Appends a new note or update to a specific incident record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The target incident ID"
                        },
                        "author_id": {
                            "type": "string",
                            "description": "User ID of the individual leaving the note"
                        },
                        "note_text": {
                            "type": "string",
                            "description": "The content of the note or update"
                        }
                    },
                    "required": ["incident_id", "author_id", "note_text"]
                }
            }
        }
