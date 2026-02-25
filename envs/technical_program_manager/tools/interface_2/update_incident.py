import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateIncident(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: str,
        status: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not incident_id:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: 'incident_id'"}
            )

        if not status:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: 'status'"}
            )

        incidents_dict = data.get("incidents", {})

        if not isinstance(incidents_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'incidents' must be a dict",
                }
            )

        incident_id_clean = str(incident_id).strip()
        status_clean = str(status).strip().lower()

        if status_clean != "acknowledged":
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid status transition. Only transition allowed is to 'acknowledged'",
                }
            )

        if incident_id_clean not in incidents_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Incident with id '{incident_id_clean}' not found",
                }
            )

        incident_record = incidents_dict[incident_id_clean]
        current_status = str(incident_record.get("status", "")).strip()

        if current_status == "acknowledged":
            return json.dumps(
                {"success": False, "error": "The incident is already acknowledged"}
            )

        if current_status not in ["open", "in_progress"]:
            return json.dumps(
                {
                    "success": False,
                    "error": "Only incidents with status 'open' or 'in_progress' can be acknowledged",
                }
            )

        incident_record["status"] = status_clean
        timestamp = "2026-02-11T23:59:00"
        incident_record["updated_at"] = timestamp

        incidents_dict[incident_id_clean] = incident_record

        response_incident = {
            "incident_id": str(incident_id_clean),
            "incident_number": str(incident_record.get("incident_number", "")),
            "incident_title": str(incident_record.get("title", "")),
            "description": str(incident_record.get("description", "")),
            "severity": str(incident_record.get("severity", "")),
            "status": str(incident_record.get("status", "")),
            "project_id": str(incident_record.get("project_id", "")),
            "work_item_id": str(incident_record.get("work_item_id", "")),
            "created_at": str(incident_record.get("created_at", "")),
            "updated_at": str(incident_record.get("updated_at", "")),
            "resolved_at": str(incident_record.get("resolved_at", "")),
            "closed_at": str(incident_record.get("closed_at", "")),
        }

        return json.dumps(
            {
                "success": True,
                "incident": response_incident,
                "message": "incident_id acknowledged successfully",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_incident",
                "description": "Acknowledges a live incident. "
                "This function validates that the incident exists and ensures "
                "the current status is 'open' or 'in_progress' before updating "
                "the status to 'acknowledged'. "
                "Use this after retrieving the incident details to acknowledge the incident.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The unique identifier of the incident.",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["acknowledged"],
                            "description": "The lifecycle status of the incident.",
                        },
                    },
                    "required": ["incident_id", "status"],
                },
            },
        }
