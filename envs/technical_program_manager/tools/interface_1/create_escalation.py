import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateEscalation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: str,
        escalated_to: str,
        escalated_by: str,
        escalation_reason: Optional[str] = None
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
        escalations = data.get("incident_escalations", {})
        
        if not incident_id or not escalated_to or not escalated_by:
            return json.dumps({
                "success": False,
                "error": "Missing parameters: incident_id, escalated_to, and escalated_by"
            })
            
        if str(incident_id) not in incidents:
            return json.dumps({
                "success": False,
                "error": f"Incident with ID '{incident_id}' not found"
            })
            
        if str(escalated_to) not in users:
            return json.dumps({
                "success": False,
                "error": f"Target user with user_id '{escalated_to}' not found"
            })
            
        if str(escalated_by) not in users:
            return json.dumps({
                "success": False,
                "error": f"Escalator user with user_id '{escalated_by}' not found"
            })
            
        new_escalation_id = generate_id(escalations)
        
        new_escalation = {
            "escalation_id": str(new_escalation_id),
            "incident_id": str(incident_id),
            "escalated_to": str(escalated_to),
            "escalated_by": str(escalated_by),
            "escalation_reason": str(escalation_reason) if escalation_reason is not None else None,
            "status": "pending",
            "created_at": "2026-02-11T23:59:00",
            "resolved_at": None
        }
        
        escalations[str(new_escalation_id)] = new_escalation
        
        escalation_response = {
            "escalation_id": str(new_escalation_id),
            "incident_id": str(incident_id),
            "escalated_to": str(escalated_to),
            "escalated_by": str(escalated_by),
            "escalation_reason": str(escalation_reason) if escalation_reason is not None else None,
            "status": "pending",
            "created_at": "2026-02-11T23:59:00",
            "resolved_at": None
        }
        
        return json.dumps({
            "success": True,
            "message": "Incident escalated successfully",
            "escalation_data": escalation_response
        })
        
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_escalation",
                "description": "Creates an escalation record for an incident, assigning it to a new responder.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The target incident ID"
                        },
                        "escalated_to": {
                            "type": "string",
                            "description": "User ID of the individual the incident is being escalated to"
                        },
                        "escalated_by": {
                            "type": "string",
                            "description": "User ID of the individual escalating the incident"
                        },
                        "escalation_reason": {
                            "type": "string",
                            "description": "The context or reason for the escalation"
                        }
                    },
                    "required": ["incident_id", "escalated_to", "escalated_by"]
                }
            }
        }
