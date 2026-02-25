import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ModifyRisk(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        risk_id: str,
        status: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not risk_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'risk_id'"
            })

        if not status:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'status'"
            })

        risks_dict = data.get("risks", {})

        if not isinstance(risks_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'risks' must be a dict"
            })

        risk_id_clean = str(risk_id).strip()
        status_clean = str(status).strip().lower()

        if risk_id_clean not in risks_dict:
            return json.dumps({
                "success": False,
                "error": f"Risk with id '{risk_id_clean}' not found"
            })

        if status_clean != "escalated":
            return json.dumps({
                "success": False,
                "error": "Only 'escalated' status update is allowed"
            })
        
        risk_record = risks_dict[risk_id_clean]
        current_status = str(risk_record.get("status", "")).strip()

        if current_status == "closed" or current_status == "escalated":
            return json.dumps({
                "success": False,
                "error": f"Risk with id '{risk_id_clean}' cannot be modified because it is already closed or escalated"
            })


        timestamp = "2026-02-11T23:59:00"

        risk_record["status"] = status_clean
        risk_record["escalated_at"] = timestamp
        risk_record["updated_at"] = timestamp

        response_risk = {
            "risk_id": str(risk_id_clean),
            "project_id": str(risk_record.get("project_id", "")),
            "description": str(risk_record.get("description", "")),
            "work_item_id": str(risk_record.get("work_item_id", "")),
            "risk_level": str(risk_record.get("risk_level", "")),
            "owner_id": str(risk_record.get("owner_id", "")),
            "status": str(risk_record.get("status", "")),
            "escalated_at": str(risk_record.get("escalated_at", "")),
            "created_at": str(risk_record.get("created_at", "")),
            "updated_at": str(risk_record.get("updated_at", ""))
        }

        return json.dumps({
            "success": True,
            "risk": response_risk,
            "message": "Risk record escalated successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_risk",
                "description":  "Escalates an existing risk record. "
                                "The function validates that the risk exists, is not closed, "
                                "and is not already escalated before updating its status to 'escalated'. "
                                "This can be used to escalate the risk in case of critical risk found or more than one risk found in a project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "risk_id": {
                            "type": "string",
                            "description": "The unique identifier of the risk record."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["escalated"],
                            "description": "The new lifecycle status of the risk."
                        }
                    },
                    "required": ["risk_id", "status"]
                }
            }
        }