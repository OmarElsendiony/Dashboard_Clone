import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateRisk(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        program_id: str,
        description: str,
        risk_level: str,
        owner_id: str,
        work_item_id: Optional[str] = None
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for risks"
            })
        
        risks = data.get("risks", {})
        projects = data.get("projects", {})
        users = data.get("users", {})
        work_items = data.get("work_items", {})
        
        if not all([program_id, description, risk_level, owner_id]):
            return json.dumps({
                "success": False,
                "error": "Missing required parameters: program_id, description, risk_level, and owner_id are required"
            })
        
        if str(program_id) not in projects:
            return json.dumps({
                "success": False,
                "error": f"Project with ID '{program_id}' not found"
            })
        
        if str(owner_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Owner with user_id '{owner_id}' not found"
            })
        
        valid_levels = ["low", "medium", "high", "critical"]
        if risk_level not in valid_levels:
            return json.dumps({
                "success": False,
                "error": f"Invalid risk_level '{risk_level}'. Must be one of: {', '.join(valid_levels)}"
            })
        
        if work_item_id and str(work_item_id) not in work_items:
            return json.dumps({
                "success": False,
                "error": f"Work item with ID '{work_item_id}' not found"
            })
        
        new_risk_id = generate_id(risks)
        
        new_risk = {
            "risk_id": str(new_risk_id),
            "project_id": str(program_id), 
            "description": str(description),
            "work_item_id": str(work_item_id) if work_item_id else None,
            "risk_level": str(risk_level),
            "owner_id": str(owner_id),
            "status": "open",
            "escalated_at": None,
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        risks[str(new_risk_id)] = new_risk
        
        risk_response = {
            "risk_id": str(new_risk_id),
            "program_id": str(program_id), 
            "description": str(description),
            "work_item_id": str(work_item_id) if work_item_id else None,
            "risk_level": str(risk_level),
            "owner_id": str(owner_id),
            "status": "open",
            "escalated_at": None,
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        return json.dumps({
            "success": True,
            "message": f"Risk created successfully with level '{risk_level}'",
            "risk_id": str(new_risk_id),
            "risk_data": risk_response
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_risk",
                "description": "Creates a new risk record. Use this when identifying program risks, documenting potential issues that could impact delivery, establishing risk ownership for mitigation tracking, or recording concerns that need monitoring.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "program_id": {
                            "type": "string",
                            "description": "Program ID the risk belongs to (required, must exist)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Risk description (required)"
                        },
                        "risk_level": {
                            "type": "string",
                            "description": "Risk level (required). Valid values: low, medium, high, critical",
                            "enum": ["low", "medium", "high", "critical"]
                        },
                        "owner_id": {
                            "type": "string",
                            "description": "User ID of the risk owner (required, must exist)"
                        },
                        "work_item_id": {
                            "type": "string",
                            "description": "Associated work item ID (optional, must exist if provided)"
                        }
                    },
                    "required": ["program_id", "description", "risk_level", "owner_id"]
                }
            }
        }
