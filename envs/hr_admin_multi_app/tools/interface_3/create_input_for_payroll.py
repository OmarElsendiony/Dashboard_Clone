import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateInputForPayroll(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        hours_worked: float,
        overtime_hours: Optional[float] = 0,
        allowance_amount: Optional[float] = 0,
    ) -> str:
        """
        Create a payroll input record for an employee in a specific cycle.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee (required).
            cycle_id: The ID of the payroll cycle (required).
            hours_worked: The number of regular hours worked (required).
            overtime_hours: The number of overtime hours worked. Defaults to 0.
            allowance_amount: The allowance amount. Defaults to 0.
        
        Returns:
            JSON string with the created payroll input record.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            max_id = 0
            for k in table.keys():
                try:
                    max_id = max(max_id, int(k))
                except ValueError:
                    continue
            return str(max_id + 1)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})
        if not cycle_id:
            return json.dumps({"error": "Missing required parameter: cycle_id is required"})
        if hours_worked is None:
            return json.dumps({"error": "Missing required parameter: hours_worked is required"})

        employee_id = str(employee_id)
        cycle_id = str(cycle_id)

        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        payroll_inputs = data.get("payroll_inputs", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        if cycle_id not in payroll_cycles:
            return json.dumps({"error": f"Payroll cycle with ID '{cycle_id}' not found"})

        cycle = payroll_cycles[cycle_id]
        if cycle.get("status") == "closed":
            return json.dumps({"error": f"Cannot add input to closed payroll cycle '{cycle_id}'"})

        # Check for existing input for this employee/cycle combination
        for input_id, pinput in payroll_inputs.items():
            if pinput.get("employee_id") == employee_id and pinput.get("cycle_id") == cycle_id:
                return json.dumps({
                    "error": f"Payroll input for employee '{employee_id}' in cycle '{cycle_id}' already exists"
                })

        # Generate new input ID
        input_id = generate_id(payroll_inputs)

        # Create payroll input record
        timestamp = "2025-11-16T23:59:00"
        new_input = {
            "input_id": input_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "hours_worked": float(hours_worked),
            "overtime_hours": float(overtime_hours or 0),
            "allowance_amount": float(allowance_amount or 0),
            "payroll_variance_percent": None,
            "status": "pending",
            "issue_field": None,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        payroll_inputs[input_id] = new_input
        data["payroll_inputs"] = payroll_inputs

        return json.dumps(new_input)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_input_for_payroll",
                "description": (
                    "Creates a payroll input record for an employee in a specific payroll cycle. "
                    "Records hours worked, overtime, and allowances for payroll processing."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee (required).",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "The ID of the payroll cycle (required).",
                        },
                        "hours_worked": {
                            "type": "number",
                            "description": "The number of regular hours worked (required).",
                        },
                        "overtime_hours": {
                            "type": "number",
                            "description": "The number of overtime hours worked. Defaults to 0.",
                        },
                        "allowance_amount": {
                            "type": "number",
                            "description": "The allowance amount. Defaults to 0.",
                        },
                    },
                    "required": ["employee_id", "cycle_id", "hours_worked"],
                },
            },
        }
