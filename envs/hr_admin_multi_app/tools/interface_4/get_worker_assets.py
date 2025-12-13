import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class GetWorkerAssets(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: Optional[str] = None,
        employee_email: Optional[str] = None
    ) -> str:
        """
        Get worker assets. Requires either employee_id or employee_email.
        """
        employee_assets = data.get("employee_assets", {})
        employees = data.get("employees", {})
        
        # Validate at least one identifier is provided
        if not employee_id and not employee_email:
            return json.dumps({
                "success": False,
                "error": "Either employee_id or employee_email must be provided",
                "count": 0,
                "assets": []
            })
        
        # If employee_email is provided, find the employee_id
        target_employee_id = employee_id
        if employee_email and not employee_id:
            target_employee_id = None
            for emp_id, employee in employees.items():
                if employee.get("email") == employee_email:
                    target_employee_id = emp_id
                    break
            
            if target_employee_id is None:
                return json.dumps({
                    "success": False,
                    "error": f"employee_email '{employee_email}' does not reference a valid employee",
                    "count": 0,
                    "assets": []
                })
        
        # Validate employee exists if employee_id was provided directly
        if employee_id and employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee",
                "count": 0,
                "assets": []
            })
        
        # Filter assets by employee_id
        results = []
        for asset_id, asset in employee_assets.items():
            if asset.get("employee_id") == target_employee_id:
                results.append(asset)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "assets": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_worker_assets",
                "description": "Get worker assets. Requires either employee_id or employee_email. Returns all assets assigned to the specified employee.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (optional, either this or employee_email must be provided)"
                        },
                        "employee_email": {
                            "type": "string",
                            "description": "Employee email (optional, either this or employee_id must be provided)"
                        }
                    },
                    "required": []
                }
            }
        }
