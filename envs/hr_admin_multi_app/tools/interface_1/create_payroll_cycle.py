import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreatePayrollCycle(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        start_date: str,
        end_date: str,
        frequency: str,
        status: str = "open",
    ) -> str:
        """
        Creates a new payroll cycle record.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not start_date or not end_date or not frequency:
            return json.dumps(
                {
                    "error": "Missing required parameters: start_date, end_date, and frequency are required"
                }
            )

        # Validate that start_date is not after end_date
        if start_date > end_date:
            return json.dumps(
                {"error": "Invalid date range: start_date cannot be after end_date"}
            )

        allowed_statuses = ["open", "closed"]
        if status not in allowed_statuses:
            return json.dumps(
                {"error": "Invalid status. Allowed values: 'open', 'closed'"}
            )

        payroll_cycles = data.setdefault("payroll_cycles", {})
        # Enforce uniqueness of (start_date, end_date)
        for existing_cycle in payroll_cycles.values():
            if (
                existing_cycle.get("start_date") == start_date
                and existing_cycle.get("end_date") == end_date
            ):
                return json.dumps(
                    {
                        "error": "A payroll cycle with the same start_date and end_date already exists"
                    }
                )

        timestamp = "2025-11-16T23:59:00"
        new_cycle_id = generate_id(payroll_cycles)
        new_cycle = {
            "cycle_id": new_cycle_id,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        payroll_cycles[new_cycle_id] = new_cycle

        return json.dumps(new_cycle)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_payroll_cycle",
                "description": (
                    "Creates a new payroll cycle in the HR payroll system. "
                    "Each payroll cycle is uniquely identified by its start_date and end_date combination, "
                    "and includes metadata such as frequency and status. Use this tool to define a new cycle "
                    "for which payroll inputs, earnings, payslips, and payments will be associated."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": (
                                "Start date of the payroll cycle in format (YYYY-MM-DD). "
                                "Required parameter."
                            ),
                        },
                        "end_date": {
                            "type": "string",
                            "description": (
                                "End date of the payroll cycle in format (YYYY-MM-DD). "
                                "Required parameter."
                            ),
                        },
                        "frequency": {
                            "type": "string",
                            "description": (
                                "Frequency label of the payroll cycle (for example: 'monthly', 'bi-weekly', 'weekly'). "
                                "This is a required free-text field used for categorization."
                            ),
                        },
                        "status": {
                            "type": "string",
                            "description": (
                                "Initial status of the payroll cycle. "
                                "Allowed values: 'open', 'closed'. "
                                "Defaults to 'open' when not explicitly provided."
                            ),
                        },
                    },
                    "required": ["start_date", "end_date", "frequency"],
                },
            },
        }
