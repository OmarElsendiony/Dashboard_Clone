import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CompleteOffboarding(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str
    ) -> str:
        """
        Complete offboarding by updating exit clearance status to 'cleared'.
        Validates exit case exists for the employee.
        """
        exit_cases = data.get("exit_cases", {})
        employees = data.get("employees", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required field
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        # Find exit case for this employee
        exit_case = None
        exit_case_id = None
        for case_id, case in exit_cases.items():
            if case.get("employee_id") == employee_id:
                exit_case = case
                exit_case_id = case_id
                break
        
        if exit_case is None:
            return json.dumps({
                "success": False,
                "error": f"No exit case found for employee_id '{employee_id}'"
            })
        
        # Update exit clearance status to 'cleared'
        exit_case["exit_clearance_status"] = "cleared"
        exit_case["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "exit_case": exit_case
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "complete_offboarding",
                "description": "Complete offboarding by updating exit clearance status to 'cleared' for the specified employee. Validates exit case exists for the employee.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        }
                    },
                    "required": ["employee_id"]
                }
            }
        }
