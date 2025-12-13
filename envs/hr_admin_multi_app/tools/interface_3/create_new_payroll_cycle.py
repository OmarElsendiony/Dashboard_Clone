import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class CreateNewPayrollCycle(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        start_date: str,
        end_date: str,
        frequency: str,
        status: str = "open",
    ) -> str:
        """
        Create a new payroll cycle.
        
        Args:
            data: The database dictionary containing all tables.
            start_date: The start date of the cycle in format (YYYY-MM-DD) (required).
            end_date: The end date of the cycle in format (YYYY-MM-DD) (required).
            frequency: The payroll frequency (e.g., 'weekly', 'bi-weekly', 'monthly') (required).
            status: The cycle status. Allowed values: 'open', 'closed'. Defaults to 'open'.
        
        Returns:
            JSON string with the created payroll cycle record.
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

        if not start_date:
            return json.dumps({"error": "Missing required parameter: start_date is required"})
        if not end_date:
            return json.dumps({"error": "Missing required parameter: end_date is required"})
        if not frequency:
            return json.dumps({"error": "Missing required parameter: frequency is required"})

        # Validate status
        allowed_statuses = ["open", "closed"]
        if status not in allowed_statuses:
            return json.dumps({
                "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
            })

        payroll_cycles = data.get("payroll_cycles", {})

        # Check for overlapping cycles
        for cycle_id, cycle in payroll_cycles.items():
            if cycle.get("start_date") == start_date and cycle.get("end_date") == end_date:
                return json.dumps({
                    "error": f"Payroll cycle with dates {start_date} to {end_date} already exists"
                })

        # Generate new cycle ID
        cycle_id = generate_id(payroll_cycles)

        # Create payroll cycle record
        timestamp = "2025-11-16T23:59:00"
        new_cycle = {
            "cycle_id": cycle_id,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        payroll_cycles[cycle_id] = new_cycle
        data["payroll_cycles"] = payroll_cycles

        return json.dumps(new_cycle)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_payroll_cycle",
                "description": (
                    "Creates a new payroll cycle for a specific date range. "
                    "Each date range can only have one payroll cycle."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "The start date of the cycle in format (YYYY-MM-DD) (required).",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "The end date of the cycle in format (YYYY-MM-DD) (required).",
                        },
                        "frequency": {
                            "type": "string",
                            "description": "The payroll frequency (e.g., 'weekly', 'bi-weekly', 'monthly') (required).",
                        },
                        "status": {
                            "type": "string",
                            "description": "The cycle status. Allowed values: 'open', 'closed'. Defaults to 'open'.",
                        },
                    },
                    "required": ["start_date", "end_date", "frequency"],
                },
            },
        }
