import json
from typing import Any, Dict
from datetime import datetime
from tau_bench.envs.tool import Tool


class StartNewPayrollCycle(Tool):
    """
    Create a new payroll cycle.
    - Creates a new payroll cycle with specified start date, end date, and frequency.
    - Validates that end date is after start date.
    - Validates that no overlapping cycle exists for the same date range.
    - Sets initial status as 'open'.
    - Returns the created cycle details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        start_date: str,
        end_date: str,
        frequency: str,
        status: str = "open",
    ) -> str:

        timestamp = "2025-11-16T23:59:00"

        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        payroll_cycles_dict = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
                }
            )

        # Validate status
        valid_statuses = ["open", "closed"]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Validate required parameters
        if not start_date:
            return json.dumps({"success": False, "error": "start_date is required"})

        if not end_date:
            return json.dumps({"success": False, "error": "end_date is required"})

        if not frequency:
            return json.dumps({"success": False, "error": "frequency is required"})

        # Validate date format and that end_date is after start_date
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            if end_dt <= start_dt:
                return json.dumps(
                    {
                        "success": False,
                        "error": "end_date must be after start_date",
                    }
                )
        except ValueError as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid date format. Expected YYYY-MM-DD format. Error: {str(e)}",
                }
            )

        # Check for overlapping cycles with the same start_date and end_date (per schema unique constraint)
        for cycle_id, cycle in payroll_cycles_dict.items():
            if not isinstance(cycle, dict):
                continue

            existing_start = cycle.get("start_date")
            existing_end = cycle.get("end_date")

            if existing_start and existing_end:
                # Check if there's any overlap between date ranges
                # Overlap occurs if: new_start <= existing_end AND new_end >= existing_start
                if start_date <= existing_end and end_date >= existing_start:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Payroll cycle dates overlap with existing cycle '{cycle_id}' (existing: {existing_start} to {existing_end}, new: {start_date} to {end_date})",
                        }
                    )

        # Generate new cycle_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_cycle_id = generate_id(payroll_cycles_dict)

        # Create new payroll cycle
        new_cycle = {
            "cycle_id": new_cycle_id,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        # Add to data
        payroll_cycles_dict[new_cycle_id] = new_cycle

        return json.dumps(
            {
                "success": True,
                "payroll_cycle": new_cycle,
                "message": f"Payroll cycle created successfully with ID: {new_cycle_id}",
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
                "name": "start_new_payroll_cycle",
                "description": (
                    "Create a new payroll cycle with specified date range and frequency. "
                    "Validates that end_date is after start_date and that no overlapping cycle is created "
                    "exists for the same date range. Sets initial status as 'open'. "
                    "Returns the created cycle details including the generated cycle_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "The start date of the payroll cycle in YYYY-MM-DD format.",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "The end date of the payroll cycle in YYYY-MM-DD format. Must be after start_date.",
                        },
                        "frequency": {
                            "type": "string",
                            "description": "The payroll frequency (e.g., 'weekly', 'bi-weekly', 'monthly', 'semi-monthly').",
                        },
                        "status": {
                            "type": "string",
                            "description": "Accepted values: open, closed (optional, default: 'open')",
                        },
                    },
                    "required": ["start_date", "end_date", "frequency"],
                },
            },
        }
