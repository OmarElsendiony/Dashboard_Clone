import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AssignOnboardingJourney(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: str,
        employee_id: str
    ) -> str:
        """
        Assign an onboarding journey (checklist) to an employee.
        Validates the journey exists and is active (pending status).
        """
        checklists = data.get("checklists", {})
        employees = data.get("employees", {})
        timestamp = "2025-12-12T12:00:00"
        
        # Validate required fields
        if not checklist_id:
            return json.dumps({
                "success": False,
                "error": "checklist_id is required"
            })
        
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        # Validate checklist exists
        if checklist_id not in checklists:
            return json.dumps({
                "success": False,
                "error": f"checklist_id '{checklist_id}' does not reference a valid checklist"
            })
        
        checklist = checklists[checklist_id]
        
        # Validate checklist is onboarding type
        if checklist.get("checklist_type") != "onboarding":
            return json.dumps({
                "success": False,
                "error": f"checklist_id '{checklist_id}' is not an onboarding journey"
            })
        
        # Validate checklist is active (pending status, not completed)
        if checklist.get("status") != "pending":
            return json.dumps({
                "success": False,
                "error": f"checklist_id '{checklist_id}' is not active (status is '{checklist.get('status')}', must be 'pending')"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        employee = employees[employee_id]
        
        # Validate employee is active
        if employee.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' is not active (status is '{employee.get('status')}')"
            })
        
        # Check if employee already has a checklist (employee_id is unique in schema)
        for chk_id, chk in checklists.items():
            if chk_id != checklist_id and chk.get("employee_id") == employee_id:
                return json.dumps({
                    "success": False,
                    "error": f"employee_id '{employee_id}' already has a checklist (checklist_id: '{chk_id}')"
                })
        
        # Assign checklist to employee
        checklist["employee_id"] = employee_id
        checklist["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "checklist": checklist
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_onboarding_journey",
                "description": "Assign an onboarding journey (checklist) to an employee. Validates the journey exists, is active (pending status), and the employee is active. Each employee can only have one checklist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "Checklist ID to assign (required)"
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID to assign the journey to (required)"
                        }
                    },
                    "required": ["checklist_id", "employee_id"]
                }
            }
        }
