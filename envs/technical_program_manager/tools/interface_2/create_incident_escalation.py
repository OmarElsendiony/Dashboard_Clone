import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateIncidentEscalation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: str,
        escalated_to: str,
        escalated_by: str,
        escalation_reason: str,
    ) -> str:

        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        for name, value in [
            ("incident_id", incident_id),
            ("escalated_to", escalated_to),
            ("escalated_by", escalated_by),
            ("escalation_reason", escalation_reason),
        ]:
            if not value or not str(value).strip():
                return json.dumps({
                    "success": False,
                    "error": f"Missing required parameter: '{name}'"
                })

        incidents_dict = data.get("incidents", {})
        users_dict = data.get("users", {})
        escalations_dict = data.get("incident_escalations", {})

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

        if not isinstance(escalations_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'incident_escalations' must be a dict"
            })

        incident_id_clean = str(incident_id).strip()
        escalated_to_clean = str(escalated_to).strip()
        escalated_by_clean = str(escalated_by).strip()
        escalation_reason_clean = str(escalation_reason).strip()

        if incident_id_clean not in incidents_dict:
            return json.dumps({
                "success": False,
                "error": f"Incident with ID '{incident_id_clean}' not found"
            })

        if escalated_to_clean not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with user_id '{escalated_to_clean}' not found"
            })

        if escalated_by_clean not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with user_id '{escalated_by_clean}' not found"
            })
        
        if str(users_dict[escalated_to_clean].get("status", "")).strip().lower() != "active":
            return json.dumps({
                "success": False,
                "error": f"User with user_id '{escalated_to_clean}' is not active"
            })

        if str(users_dict[escalated_by_clean].get("status", "")).strip().lower() != "active":
            return json.dumps({
                "success": False,
                "error": f"User with user_id '{escalated_by_clean}' is not active"
            })
        for esc in escalations_dict.values():
            if (
                str(esc.get("incident_id", "")).strip() == incident_id_clean
                and str(esc.get("escalated_to", "")).strip() == escalated_to_clean
        ):
                return json.dumps({
                "success": False,
                "error": f"An escalation already exists for incident_id '{incident_id_clean}' and user_id '{escalated_to_clean}'"
        })

        new_id = generate_id(escalations_dict)

        escalation_record = {
            "escalation_id": str(new_id),
            "incident_id": str(incident_id_clean),
            "escalated_to": str(escalated_to_clean),
            "escalated_by": str(escalated_by_clean),
            "escalation_reason": str(escalation_reason_clean),
            "status": "pending",
            "created_at": timestamp,
            "resolved_at": None,
        }

        escalations_dict[new_id] = escalation_record

        return json.dumps({
            "success": True,
            "incident_escalation": escalation_record
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_incident_escalation",
                "description":
                    "Creates an escalation record for an incident when additional attention or authority is required. "
                    "Use this during incident management workflows after reviewing incident severity and impact "
                    "to formally escalate responsibility and track escalation actions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The unique identifier of the incident."
                        },
                        "escalated_to": {
                            "type": "string",
                            "description": "The user_id of the person the incident is escalated to."
                        },
                        "escalated_by": {
                            "type": "string",
                            "description": "The user_id of the person initiating the escalation."
                        },
                        "escalation_reason": {
                            "type": "string",
                            "description": "Reason explaining why the incident is being escalated."
                        }
                    },
                    "required": [
                        "incident_id",
                        "escalated_to",
                        "escalated_by",
                        "escalation_reason"
                    ]
                }
            }
        }