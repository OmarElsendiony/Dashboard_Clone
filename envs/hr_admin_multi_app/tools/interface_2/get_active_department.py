import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetActiveDepartment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        department_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve active department details from the HR database.
        Returns department information if the department exists and has status "active".
        """
        if not isinstance(data, dict):
            return {
                "success": False,
                "error": "Invalid data format"
            }

        departments = data.get("departments", {})
        
        if not department_id:
            return {
                "success": False,
                "error": "department_id is required"
            }

        department = departments.get(department_id)
        
        if not department:
            return {
                "success": False,
                "error": f"Department with id '{department_id}' not found"
            }

        status = department.get("status")
        
        if status != "active":
            return {
                "success": False,
                "error": f"Department with id '{department_id}' is not active. Current status: '{status}'"
            }

        return {
            "success": True,
            "department": {
                "department_id": department.get("department_id"),
                "name": department.get("name"),
                "status": department.get("status"),
                "head_of_department_id": department.get("head_of_department_id"),
                "created_at": department.get("created_at"),
                "last_updated": department.get("last_updated")
            }
        }

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_active_department",
                "description": "Retrieve active department details. Returns department information if the department exists and has status 'active'. Returns an error if the department is not found or is not active.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "department_id": {
                            "type": "string",
                            "description": "Unique department identifier",
                        },
                    },
                    "required": ["department_id"],
                },
            },
        }

