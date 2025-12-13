import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateJourney(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_type: str,
        employee_id: str,
        status: Optional[str] = "pending"
    ) -> str:
        """
        Create a new journey (checklist) for an employee.
        """
        checklists = data.get("checklists", {})
        employees = data.get("employees", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required fields
        if not checklist_type:
            return json.dumps({
                "success": False,
                "error": "checklist_type is required"
            })
        
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        # Validate checklist_type
        valid_checklist_types = ["onboarding", "offboarding"]
        if checklist_type not in valid_checklist_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid checklist_type. Must be one of: {', '.join(valid_checklist_types)}"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        # Check if employee already has a checklist (employee_id is unique in schema)
        for checklist_id, checklist in checklists.items():
            if checklist.get("employee_id") == employee_id:
                existing_type = checklist.get("checklist_type")
                return json.dumps({
                    "success": False,
                    "error": f"Employee '{employee_id}' already has a checklist of type '{existing_type}'. Each employee can only have one checklist."
                })
        
        # Validate status if provided
        valid_statuses = ["pending", "completed"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Generate new checklist_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_checklist_id = generate_id(checklists)
        
        # Create new checklist record
        new_checklist = {
            "checklist_id": new_checklist_id,
            "checklist_type": checklist_type,
            "employee_id": employee_id,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        checklists[new_checklist_id] = new_checklist
        
        return json.dumps({
            "success": True,
            "checklist": new_checklist
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_journey",
                "description": "Create a new journey (checklist) for an employee. Validates employee exists and checklist_type is valid. Each employee can only have one checklist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_type": {
                            "type": "string",
                            "description": "Type of checklist: onboarding, offboarding (required)",
                            "enum": ["onboarding", "offboarding"]
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the checklist: pending, completed (optional, default: 'pending')",
                            "enum": ["pending", "completed"]
                        }
                    },
                    "required": ["checklist_type", "employee_id"]
                }
            }
        }
