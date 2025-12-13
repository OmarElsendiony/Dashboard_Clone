import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class GetWorkerProfile(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: Optional[str] = None,
        employee_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        department_id: Optional[str] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        role: Optional[str] = None
    ) -> str:
        """
        Get worker (employee) profile(s) based on filter criteria.
        Returns all workers that match the specified filters.
        """
        employees = data.get("employees", {})
        departments = data.get("departments", {})
        results = []
        
        # Validate department_id if provided
        if department_id and department_id not in departments:
            return json.dumps({
                "success": False,
                "error": f"department_id '{department_id}' does not reference a valid department",
                "count": 0,
                "workers": []
            })
        
        # Validate manager_id if provided
        if manager_id and manager_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"manager_id '{manager_id}' does not reference a valid employee",
                "count": 0,
                "workers": []
            })
        
        for emp_id, employee in employees.items():
            match = True
            
            if email and employee.get("email") != email:
                match = False
            if employee_id and emp_id != employee_id:
                match = False
            if manager_id and employee.get("manager_id") != manager_id:
                match = False
            if department_id and employee.get("department_id") != department_id:
                match = False
            if status and employee.get("status") != status:
                match = False
            if location and employee.get("location") != location:
                match = False
            if role and employee.get("role") != role:
                match = False
            
            if match:
                # Create a copy of the employee to avoid modifying the original
                worker_profile = employee.copy()
                results.append(worker_profile)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "workers": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_worker_profile",
                "description": "Get worker (employee) profile(s) based on filter criteria. Returns all workers that match the specified filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Filter by email address (optional)"
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Filter by employee ID (optional)"
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "Filter by manager ID (optional)"
                        },
                        "department_id": {
                            "type": "string",
                            "description": "Filter by department ID (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: active, inactive, on_leave, probation (optional)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Filter by location (optional)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Filter by role: admin, non_admin (optional)"
                        }
                    },
                    "required": []
                }
            }
        }
