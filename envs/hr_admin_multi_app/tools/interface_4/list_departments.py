import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class ListDepartments(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        department_id: Optional[str] = None,
        name: Optional[str] = None,
        status: str = 'active',
        head_of_department_id: Optional[str] = None
    ) -> str:
        """
        List department(s) based on filter criteria.
        Returns all departments that match the specified filters.
        """
        departments = data.get("departments", {})
        employees = data.get("employees", {})
        results = []
        
        # Validate head_of_department_id if provided
        if head_of_department_id and head_of_department_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"head_of_department_id '{head_of_department_id}' does not reference a valid employee",
                "count": 0,
                "departments": []
            })
        
        for dept_id, department in departments.items():
            match = True
            
            if department_id and dept_id != department_id:
                match = False
            if name and department.get("name") != name:
                match = False
            if status and department.get("status") != status:
                match = False
            if head_of_department_id and department.get("head_of_department_id") != head_of_department_id:
                match = False
            
            if match:
                # Create a copy of the department to avoid modifying the original
                department_info = department.copy()
                results.append(department_info)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "departments": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_departments",
                "description": "List department(s) based on filter criteria. Returns all departments that match the specified filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "department_id": {
                            "type": "string",
                            "description": "Filter by department ID (optional)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Filter by department name (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: active, inactive (optional, default: 'active')"
                        },
                        "head_of_department_id": {
                            "type": "string",
                            "description": "Filter by head of department employee ID (optional)"
                        }
                    },
                    "required": []
                }
            }
        }
