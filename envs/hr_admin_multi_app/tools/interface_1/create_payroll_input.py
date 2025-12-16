import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreatePayrollInput(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        hours_worked: float,
        overtime_hours: float = 0.0,
        allowance_amount: float = 0.0,
    ) -> str:
        """
        Creates a new payroll input record for an employee in a given payroll cycle.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id or not cycle_id:
            return json.dumps(
                {
                    "error": "Missing required parameters: employee_id and cycle_id are required"
                }
            )

        # Convert IDs to strings for consistent comparison
        employee_id = str(employee_id)
        cycle_id = str(cycle_id)

        if hours_worked is None:
            return json.dumps(
                {"error": "Missing required parameter: hours_worked is required"}
            )

        if hours_worked < 0 or overtime_hours < 0 or allowance_amount < 0:
            return json.dumps(
                {
                    "error": "hours_worked, overtime_hours, and allowance_amount must be non-negative numbers"
                }
            )

        employees = data.get("employees", {})
        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        employee = employees[employee_id]
        base_salary = employee.get("base_salary", 0)

        payroll_cycles = data.get("payroll_cycles", {})
        if cycle_id not in payroll_cycles:
            return json.dumps(
                {"error": f"Payroll cycle with ID '{cycle_id}' not found"}
            )

        cycle = payroll_cycles[cycle_id]
        if cycle.get("status") != "open":
            return json.dumps(
                {
                    "error": "Payroll input can only be created for a payroll cycle with status 'open'"
                }
            )

        # SOP 8, Step 4a: Validate hours worked per week (≤60 hours)
        total_hours = hours_worked + overtime_hours
        # Assuming the cycle is for one week or we check total hours directly
        if total_hours > 60:
            employee["flag_potential_overtime_violation"] = True
            return json.dumps(
                {
                    "error": "Total hours (hours_worked + overtime_hours) exceed 60 hours per week. "
                    "Employee flag 'flag_potential_overtime_violation' has been set. "
                    "Please review before creating payroll input."
                }
            )

        # SOP 8, Step 4b: Validate allowance amount (< 25% of base salary)
        if base_salary > 0 and allowance_amount >= (0.25 * base_salary):
            employee["flag_requires_payroll_review"] = True
            return json.dumps(
                {
                    "error": f"Allowance amount ({allowance_amount}) is >= 25% of base salary ({base_salary}). "
                    "Employee flag 'flag_requires_payroll_review' has been set. "
                    "Please review before creating payroll input."
                }
            )

        payroll_inputs = data.setdefault("payroll_inputs", {})
        timestamp = "2025-11-16T23:59:00"
        new_input_id = generate_id(payroll_inputs)

        new_input = {
            "input_id": new_input_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "hours_worked": hours_worked,
            "overtime_hours": overtime_hours,
            "allowance_amount": allowance_amount,
            "payroll_variance_percent": None,
            "status": "pending",
            "issue_field": None,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        payroll_inputs[new_input_id] = new_input

        return json.dumps(new_input)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_payroll_input",
                "description": (
                    "Creates a new payroll input record for an employee within a specific open payroll cycle. "
                    "Payroll inputs capture hours worked, overtime hours, and allowance amounts that will feed into "
                    "downstream payroll calculations and reviews. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": (
                                "ID of the employee for whom the payroll input is being created (required)."
                            ),
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": (
                                "ID of the payroll cycle to which this input belongs (required). "
                                "The cycle must exist and have status 'open'."
                            ),
                        },
                        "hours_worked": {
                            "type": "number",
                            "description": (
                                "Number of regular hours worked in the cycle (required). "
                                "Must be a non-negative number."
                            ),
                        },
                        "overtime_hours": {
                            "type": "number",
                            "description": (
                                "Number of overtime hours worked in the cycle (optional). "
                                "Defaults to 0.0 and must be a non-negative number."
                            ),
                        },
                        "allowance_amount": {
                            "type": "number",
                            "description": (
                                "Total allowance amount for the cycle (optional). "
                                "Defaults to 0.0 and must be a non-negative number."
                            ),
                        },
                    },
                    "required": ["employee_id", "cycle_id", "hours_worked"],
                },
            },
        }
