import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class UpdateCompensation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        base_salary: float,
    ) -> str:
        """
        Update an employee's base compensation/salary.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee (required).
            base_salary: The new base salary amount (required).
        
        Returns:
            JSON string with the updated employee record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})
        if base_salary is None:
            return json.dumps({"error": "Missing required parameter: base_salary is required"})

        employee_id = str(employee_id)
        employees = data.get("employees", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        if float(base_salary) < 0:
            return json.dumps({"error": "base_salary cannot be negative"})

        employee = employees[employee_id]
        employee["base_salary"] = float(base_salary)
        employee["last_updated"] = "2025-11-16T23:59:00"

        return json.dumps(employee)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_compensation",
                "description": (
                    "Updates an employee's base compensation/salary. "
                    "Use this for salary adjustments, raises, or compensation changes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee (required).",
                        },
                        "base_salary": {
                            "type": "number",
                            "description": "The new base salary amount (required).",
                        },
                    },
                    "required": ["employee_id", "base_salary"],
                },
            },
        }
