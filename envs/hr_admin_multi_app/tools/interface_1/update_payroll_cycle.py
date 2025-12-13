import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdatePayrollCycle(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cycle_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Updates an existing payroll cycle record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not cycle_id:
            return json.dumps({"error": "cycle_id is required"})

        # Convert IDs to strings for consistent comparison
        cycle_id = str(cycle_id)

        payroll_cycles = data.get("payroll_cycles", {})
        if cycle_id not in payroll_cycles:
            return json.dumps(
                {"error": f"Payroll cycle with ID '{cycle_id}' not found"}
            )

        if (
            start_date is None
            and end_date is None
            and frequency is None
            and status is None
        ):
            return json.dumps(
                {"error": "No fields provided to update. Provide at least one field"}
            )

        allowed_statuses = ["open", "closed"]
        if status is not None and status not in allowed_statuses:
            return json.dumps(
                {
                    "error": "Invalid status. Allowed values: 'open', 'closed'"
                }
            )

        current_cycle = payroll_cycles[cycle_id]

        # Validate uniqueness for updated (start_date, end_date)
        new_start = start_date if start_date is not None else current_cycle.get(
            "start_date"
        )
        new_end = end_date if end_date is not None else current_cycle.get("end_date")

        # Validate that start_date is not after end_date
        if new_start > new_end:
            return json.dumps(
                {
                    "error": "Invalid date range: start_date cannot be after end_date"
                }
            )

        for other_id, other_cycle in payroll_cycles.items():
            if other_id == cycle_id:
                continue
            if (
                other_cycle.get("start_date") == new_start
                and other_cycle.get("end_date") == new_end
            ):
                return json.dumps(
                    {
                        "error": "Another payroll cycle already exists with the same start_date and end_date"
                    }
                )

        if start_date is not None:
            current_cycle["start_date"] = start_date
        if end_date is not None:
            current_cycle["end_date"] = end_date
        if frequency is not None:
            current_cycle["frequency"] = frequency
        if status is not None:
            current_cycle["status"] = status

        timestamp = "2025-11-22T12:00:00"
        current_cycle["last_updated"] = timestamp

        return json.dumps(current_cycle)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_payroll_cycle",
                "description": (
                    "Updates fields on an existing payroll cycle. "
                    "Can modify the start_date, end_date, frequency, and status while ensuring "
                    "that no other cycle shares the same (start_date, end_date) combination."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cycle_id": {
                            "type": "string",
                            "description": "ID of the payroll cycle to update (required).",
                        },
                        "start_date": {
                            "type": "string",
                            "description": (
                                "Updated start date for the payroll cycle in format (YYYY-MM-DD). "
                                "Optional; only applied when provided."
                            ),
                        },
                        "end_date": {
                            "type": "string",
                            "description": (
                                "Updated end date for the payroll cycle in format (YYYY-MM-DD). "
                                "Optional; only applied when provided."
                            ),
                        },
                        "frequency": {
                            "type": "string",
                            "description": (
                                "Updated frequency label for the payroll cycle (for example: 'monthly', 'bi-weekly'). "
                                "Optional; only applied when provided."
                            ),
                        },
                        "status": {
                            "type": "string",
                            "description": (
                                "Updated status of the payroll cycle. "
                                "Allowed values: 'open', 'closed'. "
                                "Optional; only applied when provided."
                            ),
                        },
                    },
                    "required": ["cycle_id"],
                },
            },
        }
