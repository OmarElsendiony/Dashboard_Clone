import json
import re
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AttachIncidentNote(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: str,
        author_id: str,
        note_text: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for incident_notes"}
            )

        if incident_id is None:
            return json.dumps({"success": False, "error": "incident_id is required"})

        if author_id is None:
            return json.dumps({"success": False, "error": "author_id is required"})

        if not note_text or not note_text.strip():
            return json.dumps(
                {"success": False, "error": "note_text is required and cannot be empty"}
            )

        # Validate note_text format (policy requirement)
        note_format_pattern = re.compile(
            r"^Phase:\s+(Investigation|Mitigation|Resolution)\s+\|\s+Observation:\s+.+?\s+\|\s+Action:\s+.+$",
            re.DOTALL,
        )
        if not note_format_pattern.match(note_text):
            return json.dumps(
                {
                    "success": False,
                    "error": "note_text must follow the required format: 'Phase: Investigation | Observation: [Technical detail] | Action: [Step taken]' (Phase must be exactly 'Investigation', 'Mitigation', or 'Resolution'). Example: 'Phase: Investigation | Observation: Database connection timeout detected | Action: Restarted database service'",
                }
            )

        incidents = data.get("incidents", {})
        incident = None
        incident_key_str = str(incident_id)

        if incident_key_str in incidents:
            incident_data = incidents[incident_key_str]
            if str(incident_data.get("incident_id")) == str(incident_id):
                incident = incident_data

        if not incident:
            for _incident_key, incident_data in incidents.items():
                if str(incident_data.get("incident_id")) == str(incident_id):
                    incident = incident_data
                    break

        if not incident:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Incident with ID {str(incident_id)} not found",
                }
            )

        users = data.get("users", {})
        author_exists = False

        for _user_key, user_data in users.items():
            if str(user_data.get("user_id")) == str(author_id):
                author_exists = True
                break

        if not author_exists:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID {str(author_id)} not found in users table",
                }
            )

        # Generate note_id
        def generate_id(table: Dict[str, Any]) -> int:
            if not table:
                return 1
            return max(int(k) for k in table.keys()) + 1

        incident_notes = data.setdefault("incident_notes", {})
        note_id = generate_id(incident_notes)
        timestamp = "2026-02-11T23:59:00"

        new_note = {
            "note_id": str(note_id),
            "incident_id": str(incident_id),
            "author_id": str(author_id),
            "note_text": str(note_text),
            "created_at": str(timestamp),
        }

        incident_notes[str(note_id)] = new_note

        return json.dumps(
            {
                "success": True,
                "note": new_note,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "attach_incident_note",
                "description": "Attach a note to an incident. Use this to add progress updates, troubleshooting notes, resolution details, or any other information relevant to incident management and tracking.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The incident ID to attach the note to",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The user ID of the person creating the note",
                        },
                        "note_text": {
                            "type": "string",
                            "description": "The content of the note. Must follow the required format: 'Phase: Investigation | Observation: [Technical detail] | Action: [Step taken]' where Phase must be exactly 'Investigation', 'Mitigation', or 'Resolution'. Example: 'Phase: Investigation | Observation: Database connection timeout detected | Action: Restarted database service'",
                        },
                    },
                    "required": ["incident_id", "author_id", "note_text"],
                },
            },
        }
