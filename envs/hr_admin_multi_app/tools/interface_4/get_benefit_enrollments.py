import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool

class GetBenefitEnrollments(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str
    ) -> str:
        """
        Get benefit enrollment(s) for an employee.
        Returns all benefit enrollments for the specified employee.
        """
        benefit_enrollments = data.get("benefit_enrollments", {})
        employees = data.get("employees", {})
        results = []
        
        # Validate required field
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required",
                "count": 0,
                "enrollments": []
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee",
                "count": 0,
                "enrollments": []
            })
        
        # Filter enrollments by employee_id
        for enrollment_id, enrollment in benefit_enrollments.items():
            if enrollment.get("employee_id") == employee_id:
                # Create a copy of the enrollment to avoid modifying the original
                enrollment_copy = enrollment.copy()
                results.append(enrollment_copy)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "enrollments": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_benefit_enrollments",
                "description": "Get benefit enrollment(s) for an employee. Returns all benefit enrollments for the specified employee.",
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
