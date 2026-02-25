import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateIncidentNote(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: str,
        note_text: str,
        author_id: str,
    ) -> str:

        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not incident_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'incident_id'"
            })

        if not note_text:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'note_text'"
            })

        if not author_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'author_id'"
            })

        incidents_dict = data.get("incidents", {})
        users_dict = data.get("users", {})
        incident_notes_dict = data.get("incident_notes", {})

        if not isinstance(incidents_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'incidents' must be a dict"
            })

        if not isinstance(users_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'users' must be a dict"
            })

        if not isinstance(incident_notes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'incident_notes' must be a dict"
            })

        incident_id_clean = str(incident_id).strip()
        author_id_clean = str(author_id).strip()
        note_text_clean = str(note_text).strip()

        if incident_id_clean not in incidents_dict:
            return json.dumps({
                "success": False,
                "error": f"Incident with ID '{incident_id_clean}' not found"
            })

        author_data = users_dict.get(author_id_clean)
        if not author_data:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{author_id_clean}' not found"
            })

        if str(author_data.get("status", "")).strip() != "active":
            return json.dumps({
                "success": False,
                "error": "Inactive user cannot create incident note"
            })

        new_note_id = generate_id(incident_notes_dict)

        incident_notes_dict[new_note_id] = {
            "note_id": str(new_note_id),
            "incident_id": str(incident_id_clean),
            "author_id": str(author_id_clean),
            "note_text": str(note_text_clean),
            "created_at": timestamp
        }

        response_note = {
            "note_id": str(new_note_id),
            "incident_id": str(incident_id_clean),
            "author_id": str(author_id_clean),
            "note_text": str(note_text_clean),
            "created_at": timestamp
        }

        return json.dumps({
            "success": True,
            "incident_note": response_note
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_incident_note",
                "description": "Creates a note for a specific incident to document updates, acknowledgements, "
                               "or impact summaries during incident management workflows. "
                               "Use this to formally record structured incident notes before notifying stakeholders.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The unique identifier of the incident."
                        },
                        "note_text": {
                            "type": "string",
                            "description": "The formatted note text to be recorded for the incident."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user creating the note."
                        }
                    },
                    "required": ["incident_id", "note_text", "author_id"]
                }
            }
        }
