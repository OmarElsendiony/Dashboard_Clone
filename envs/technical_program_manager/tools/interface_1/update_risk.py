import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateRisk(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        risk_id: str,
        description: Optional[str] = None,
        risk_level: Optional[str] = None,
        owner_id: Optional[str] = None,
        status: Optional[str] = None,
        escalated_at: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for risks"
            })
        
        risks = data.get("risks", {})
        users = data.get("users", {})
        
        # Validate required field
        if not risk_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: risk_id is required"
            })
        
        # Validate risk exists
        if str(risk_id) not in risks:
            return json.dumps({
                "success": False,
                "error": f"Risk with ID '{risk_id}' not found"
            })
        
        risk = risks[str(risk_id)]
        
        # At least one optional field must be provided
        if not any([description, risk_level, owner_id, status, escalated_at is not None]):
            return json.dumps({
                "success": False,
                "error": "At least one field to update must be provided"
            })
        
        # Validate owner exists if provided
        if owner_id and str(owner_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Owner with user_id '{owner_id}' not found"
            })
        
        # Validate risk_level if provided
        if risk_level:
            valid_levels = ["low", "medium", "high", "critical"]
            if risk_level not in valid_levels:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid risk_level '{risk_level}'. Must be one of: {', '.join(valid_levels)}"
                })
        
        # Validate status if provided
        if status:
            valid_statuses = ["open", "closed", "escalated"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Update risk fields
        updated_risk = risk.copy()
        
        if description:
            updated_risk["description"] = str(description)
        if risk_level:
            updated_risk["risk_level"] = str(risk_level)
        if owner_id:
            updated_risk["owner_id"] = str(owner_id)
        if status:
            updated_risk["status"] = str(status)
        if escalated_at is not None:
            updated_risk["escalated_at"] = str(escalated_at) if escalated_at else None
        
        updated_risk["updated_at"] = "2026-02-11T23:59:00"
        
        # Update in risks data
        risks[str(risk_id)] = updated_risk
        
        return json.dumps({
            "success": True,
            "message": f"Risk '{risk_id}' updated successfully",
            "risk_id": str(risk_id),
            "risk_data": updated_risk
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_risk",
                "description": "Updates risk details and status. Use this to escalate risks to leadership, change risk severity levels, update mitigation status, reassign risk ownership, or mark risks as closed when mitigated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "risk_id": {
                            "type": "string",
                            "description": "The ID of the risk to update"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description"
                        },
                        "risk_level": {
                            "type": "string",
                            "description": "New risk level. Valid values: low, medium, high, critical",
                            "enum": ["low", "medium", "high", "critical"]
                        },
                        "owner_id": {
                            "type": "string",
                            "description": "New owner user ID"
                        },
                        "status": {
                            "type": "string",
                            "description": "New status. Valid values: open, closed, escalated",
                            "enum": ["open", "closed", "escalated"]
                        },
                        "escalated_at": {
                            "type": "string",
                            "description": "Escalation timestamp in YYYY-MM-DDTHH:MM:SS format"
                        }
                    },
                    "required": ["risk_id"]
                }
            }
        }

