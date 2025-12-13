import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AssignWorkerToDepartment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        department_id: str,
    ) -> str:
        """
        Assign a worker (employee) to a department.
        
        Args:
            data: Environment data containing employees and departments
            employee_id: ID of the employee to assign
            department_id: ID of the department to assign the employee to
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        
        employees = data.get("employees", {})
        departments = data.get("departments", {})
        
        # Validate required fields
        if not employee_id or not department_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameters: employee_id and department_id"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"Employee with ID '{employee_id}' not found"
            })
        
        # Validate department exists
        if department_id not in departments:
            return json.dumps({
                "success": False,
                "error": f"Department with ID '{department_id}' not found"
            })
        
        # Get employee record
        employee = employees[employee_id].copy()
        
        # Update department_id
        employee["department_id"] = department_id
        employee["last_updated"] = "2025-12-12T12:00:00"
        
        # Save back to data
        employees[employee_id] = employee
        
        # Return updated employee information
        return json.dumps({
            "success": True,
            "employee_id": employee_id,
            "department_id": department_id,
            "full_name": employee.get("full_name"),
            "email": employee.get("email"),
            "status": employee.get("status"),
            "last_updated": employee["last_updated"]
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_worker_to_department",
                "description": "Assign a worker (employee) to a department. Requires employee_id and department_id. Returns updated employee information including employee_id, department_id, full_name, email, status, and last_updated timestamp.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (worker) to assign to a department"
                        },
                        "department_id": {
                            "type": "string",
                            "description": "ID of the department to assign the employee to"
                        }
                    },
                    "required": ["employee_id", "department_id"]
                }
            }
        }