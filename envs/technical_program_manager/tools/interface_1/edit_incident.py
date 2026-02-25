import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class EditIncident(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: str,
        status: Optional[str] = None,
        acknowledged_at: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for incidents"
            })

        incidents = data.get("incidents", {})

        if not incident_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: incident_id"
            })

        if str(incident_id) not in incidents:
            return json.dumps({
                "success": False,
                "error": f"Incident with ID '{incident_id}' not found"
            })

        if status is None and acknowledged_at is None:
            return json.dumps({
                "success": False,
                "error": "At least one field must be provided for update: status or acknowledged_at"
            })

        if status is not None:
            valid_statuses = ["open", "in_progress", "resolved", "closed"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })

        incident = incidents[str(incident_id)]
        updated_incident = incident.copy()
        updated_incident["updated_at"] = "2026-02-11T23:59:00"

        if status is not None:
            updated_incident["status"] = str(status)
            if status == "resolved":
                updated_incident["resolved_at"] = "2026-02-11T23:59:00"

        if acknowledged_at is not None:
            updated_incident["acknowledged_at"] = str(acknowledged_at)

        incidents[str(incident_id)] = updated_incident

        incident_data = {
            "incident_id": str(incident_id),
            "incident_number": str(updated_incident.get("incident_number", "")) if updated_incident.get("incident_number") is not None else None,
            "title": str(updated_incident.get("title", "")) if updated_incident.get("title") is not None else None,
            "description": str(updated_incident.get("description", "")) if updated_incident.get("description") is not None else None,
            "severity": str(updated_incident.get("severity", "")) if updated_incident.get("severity") is not None else None,
            "status": str(updated_incident.get("status", "")) if updated_incident.get("status") is not None else None,
            "program_id": str(updated_incident.get("project_id", "")) if updated_incident.get("project_id") is not None else None,
            "page_id": str(updated_incident.get("page_id", "")) if updated_incident.get("page_id") is not None else None,
            "work_item_id": str(updated_incident.get("work_item_id", "")) if updated_incident.get("work_item_id") is not None else None,
            "acknowledged_at": str(updated_incident.get("acknowledged_at", "")) if updated_incident.get("acknowledged_at") is not None else None,
            "resolved_at": str(updated_incident.get("resolved_at", "")) if updated_incident.get("resolved_at") is not None else None,
            "created_at": str(updated_incident.get("created_at", "")) if updated_incident.get("created_at") is not None else None,
            "updated_at": str(updated_incident.get("updated_at", "")) if updated_incident.get("updated_at") is not None else None
        }

        return json.dumps({
            "success": True,
            "message": f"Incident '{incident_id}' updated successfully",
            "incident_data": incident_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "edit_incident",
                "description": "Updates an existing incident. Can be used to acknowledge, progress, resolve, or close incidents, or set the acknowledgement timestamp.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "[Required] Unique identifier of the incident to update."
                        },
                        "status": {
                            "type": "string",
                            "description": "New status of the incident.",
                            "enum": ["open", "in_progress", "resolved", "closed"]
                        },
                        "acknowledged_at": {
                            "type": "string",
                            "description": "[Optional] Timestamp of when the incident was acknowledged, in YYYY-MM-DDTHH:MM:SS format."
                        }
                    },
                    "required": ["incident_id"]
                }
            }
        }