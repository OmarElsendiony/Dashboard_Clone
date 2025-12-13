from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AssignPositionToWorker(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], employee_id: str, position: str) -> Dict[str, Any]:
        """
        Assign a position to a worker (employee).
        
        Args:
            data: The data dictionary containing all entities
            employee_id: The ID of the employee to assign the position to
            position: The position/job title to assign
            
        Returns:
            Dict containing success status and updated employee data or error message
        """
        if not isinstance(data, dict):
            return {"success": False, "error": "Invalid data format"}
        
        employees = data.get("employees", {})
        
        # Validate required fields
        if not employee_id:
            return {"success": False, "error": "Missing required parameter: employee_id"}
        
        if not position:
            return {"success": False, "error": "Missing required parameter: position"}
        
        # Validate employee exists
        if employee_id not in employees:
            return {"success": False, "error": f"Employee with ID '{employee_id}' not found"}
        
        # Update employee record with position
        employees[employee_id]["position"] = position
        employees[employee_id]["last_updated"] = "2025-11-16T23:59:00"
        
        # Return updated employee data
        updated_employee = employees[employee_id].copy()
        
        return {
            "success": True,
            "employee_id": employee_id,
            "position": position,
            "employee": updated_employee
        }
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_position_to_worker",
                "description": "Assign a position (job title) to a worker (employee). Updates the employee record with the position and returns the updated employee data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee to assign the position to"
                        },
                        "position": {
                            "type": "string",
                            "description": "The position/job title to assign to the employee"
                        }
                    },
                    "required": ["employee_id", "position"]
                }
            }
        }

