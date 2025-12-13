import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class GetWorker(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: Optional[str] = None,
        employee_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        department_id: Optional[str] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        position: Optional[str] = None,
    ) -> str:
        """
        Retrieve worker (employee) details from the HR database.
        Filters by email, employee_id, manager_id, department_id, status, location, or position.
        Returns a list of matching worker records.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        employees = data.get("employees", {})
        results = []

        for eid, employee_data in employees.items():
            match = True

            if email and employee_data.get("email") != email:
                match = False
            if employee_id and eid != employee_id:
                match = False
            if manager_id is not None:
                emp_manager_id = employee_data.get("manager_id")
                if manager_id != emp_manager_id:
                    match = False
            if department_id and employee_data.get("department_id") != department_id:
                match = False
            if status and employee_data.get("status") != status:
                match = False
            if location and employee_data.get("location") != location:
                match = False
            # Note: position field doesn't exist in employees table schema
            # If position filter is provided, it will not match any records
            # This is kept for API compatibility but will always filter out results
            if position:
                match = False

            if match:
                results.append(employee_data.copy())

        return json.dumps({"success": True, "count": len(results), "workers": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_worker",
                "description": "Retrieve worker (employee) details from the HR database. "
                "Filters by email, employee_id, manager_id, department_id, status ('active', 'inactive', 'on_leave', 'probation'), "
                "location, or position. Returns worker information including employee_id, manager_id, department_id, "
                "start_date, full_name, email, status, tenure_months, performance_rating, base_salary, location, role, "
                "and various flags.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Worker email address",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Unique employee identifier",
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "Manager's employee ID",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "Department identifier",
                        },
                        "status": {
                            "type": "string",
                            "description": "Employee status: 'active', 'inactive', 'on_leave', or 'probation'",
                        },
                        "location": {
                            "type": "string",
                            "description": "Worker location",
                        },
                        "position": {
                            "type": "string",
                            "description": "Worker position (note: position field may not be available in current schema)",
                        },
                    },
                    "required": [],
                },
            },
        }

