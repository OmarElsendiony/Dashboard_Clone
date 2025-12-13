import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class RecordCommission(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        amount: float,
    ) -> str:
        """
        Record a commission (incentive) for an employee in a payroll cycle.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee (required).
            cycle_id: The ID of the payroll cycle (required).
            amount: The commission amount (required).
        
        Returns:
            JSON string with the created payroll earning record.
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
        if amount is None:
            return json.dumps({"error": "Missing required parameter: amount is required"})

        employee_id = str(employee_id)
        cycle_id = str(cycle_id)

        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        payroll_earnings = data.get("payroll_earnings", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        if cycle_id not in payroll_cycles:
            return json.dumps({"error": f"Payroll cycle with ID '{cycle_id}' not found"})

        if float(amount) <= 0:
            return json.dumps({"error": "Commission amount must be greater than 0"})

        # Generate new earning ID
        earning_id = generate_id(payroll_earnings)

        # Create payroll earning record
        timestamp = "2025-12-12T12:00:00"
        new_earning = {
            "earning_id": earning_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "earning_type": "incentive",
            "amount": float(amount),
            "status": "pending",
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        payroll_earnings[earning_id] = new_earning
        data["payroll_earnings"] = payroll_earnings

        return json.dumps(new_earning)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "record_commission",
                "description": (
                    "Records a commission (incentive) for an employee in a specific payroll cycle. "
                    "Commissions are recorded as incentive earning type."
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
                        "amount": {
                            "type": "number",
                            "description": "The commission amount (required).",
                        },
                    },
                    "required": ["employee_id", "cycle_id", "amount"],
                },
            },
        }
