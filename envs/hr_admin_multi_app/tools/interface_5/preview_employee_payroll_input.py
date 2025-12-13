import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class PreviewEmployeePayrollInput(Tool):
    """
    Retrieve existing payroll inputs for an employee.
    - Returns all payroll inputs for a specific employee.
    - Can filter by cycle_id to get inputs for a specific payroll cycle.
    - Can filter by status (pending, review, etc.).
    - Returns payroll input details including hours, variance, and status.
    - Returns an error if the employee doesn't exist.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payroll_inputs": [...]} on success
          {"success": False, "error": "..."} on error
        """

        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        employees_dict = data.get("employees", {})
        if not isinstance(employees_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )

        payroll_inputs_dict = data.get("payroll_inputs", {})
        if not isinstance(payroll_inputs_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_inputs container: expected dict at data['payroll_inputs']",
                }
            )

        # Validate employee_id is provided
        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})

        # Convert employee_id to string for consistent comparison
        employee_id_str = str(employee_id)

        # Check if employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        # Convert cycle_id to string if provided
        cycle_id_str = str(cycle_id) if cycle_id else None

        # Retrieve payroll inputs for the employee
        employee_payroll_inputs = []

        for input_id, payroll_input in payroll_inputs_dict.items():
            if not isinstance(payroll_input, dict):
                continue

            input_employee_id = str(payroll_input.get("employee_id", ""))
            
            # Check if this input belongs to the employee
            if input_employee_id != employee_id_str:
                continue

            # Filter by cycle_id if provided
            if cycle_id_str:
                input_cycle_id = str(payroll_input.get("cycle_id", ""))
                if input_cycle_id != cycle_id_str:
                    continue

            # Filter by status if provided
            if status:
                input_status = payroll_input.get("status")
                if input_status != status:
                    continue

            # Add matching payroll input
            payroll_input_copy = payroll_input.copy()
            employee_payroll_inputs.append(payroll_input_copy)

        # Sort by created_at (most recent first) for better UX
        employee_payroll_inputs.sort(
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )

        return json.dumps(
            {
                "success": True,
                "payroll_inputs": employee_payroll_inputs,
                "count": len(employee_payroll_inputs),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "preview_employee_payroll_input",
                "description": (
                    "Retrieve existing payroll inputs for an employee. "
                    "Returns all payroll inputs for the specified employee. "
                    "Can optionally filter by cycle_id to get inputs for a specific payroll cycle. "
                    "Can optionally filter by status (pending, review, etc.). "
                    "Returns payroll input details including input_id, hours_worked, overtime_hours, "
                    "payroll_variance_percent, status, and issue_field. "
                    "Returns an error if the employee doesn't exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The employee ID to retrieve payroll inputs for.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional. Filter payroll inputs by specific cycle ID.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. Filter payroll inputs by status (e.g., 'pending', 'review').",
                        }
                    },
                    "required": ["employee_id"],
                },
            },
        }