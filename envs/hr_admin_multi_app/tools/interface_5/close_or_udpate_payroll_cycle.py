import json
from typing import Any, Dict, Optional
from datetime import datetime
from tau_bench.envs.tool import Tool


class CloseOrUpdatePayrollCycle(Tool):
    """
    Close or update an existing payroll cycle.
    - Updates the status of a payroll cycle (open, closed).
    - Can update other cycle attributes like dates or frequency.
    - Validates the cycle exists before updating.
    - Updates the last_updated timestamp.
    - Returns the updated cycle details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cycle_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        frequency: Optional[str] = None,
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

        # Validate cycle_id is provided
        if not cycle_id:
            return json.dumps({"success": False, "error": "cycle_id is required"})

        # Convert cycle_id to string for consistent comparison
        cycle_id_str = str(cycle_id)

        # Check if the cycle exists
        if cycle_id_str not in payroll_cycles_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                }
            )

        # Get the existing cycle
        cycle = payroll_cycles_dict[cycle_id_str]
        if not isinstance(cycle, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid cycle data for ID '{cycle_id_str}'",
                }
            )

        # Validate status if provided
        valid_statuses = ["open", "closed"]
        if status is not None and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Validate dates if both are provided
        if start_date and end_date:
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
        elif start_date or end_date:
            # If only one date is provided, validate format
            date_to_check = start_date if start_date is not None else end_date
            try:
                datetime.strptime(date_to_check, "%Y-%m-%d")
            except ValueError as e:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid date format. Expected YYYY-MM-DD format. Error: {str(e)}",
                    }
                )

        # Check for duplicate cycle if dates are being updated
        new_start = start_date if start_date else cycle.get("start_date")
        new_end = end_date if end_date else cycle.get("end_date")

        if start_date or end_date:
            for other_cycle_id, other_cycle in payroll_cycles_dict.items():
                if other_cycle_id == cycle_id_str:
                    continue

                if not isinstance(other_cycle, dict):
                    continue

                existing_start = other_cycle.get("start_date")
                existing_end = other_cycle.get("end_date")

                if existing_start and existing_end:
                    # Check if there's any overlap between date ranges
                    # Overlap occurs if: new_start <= existing_end AND new_end >= existing_start
                    if new_start <= existing_end and new_end >= existing_start:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Payroll cycle dates overlap with existing cycle '{cycle_id}' (existing: {existing_start} to {existing_end}, new: {start_date} to {end_date})",
                            }
                        )

        # Update the cycle with new values
        if status:
            cycle["status"] = status

        if start_date:
            cycle["start_date"] = start_date

        if end_date:
            cycle["end_date"] = end_date

        if frequency:
            cycle["frequency"] = frequency

        # Update timestamp
        cycle["last_updated"] = timestamp

        return json.dumps(
            {
                "success": True,
                "payroll_cycle": cycle,
                "message": f"Payroll cycle '{cycle_id_str}' updated successfully",
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
                "name": "close_or_update_payroll_cycle",
                "description": (
                    "Close or update an existing payroll cycle. "
                    "Validates that the cycle exists and that date changes don't overlap existing dates. "
                    "Can update the status (open, closed) and other attributes like dates or frequency. "
                    "Updates the last_updated timestamp automatically. "
                    "Returns the updated cycle details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cycle_id": {
                            "type": "string",
                            "description": "The ID of the payroll cycle to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. New status for the cycle. Accepted values: 'open', 'closed'.",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Optional. New start date in YYYY-MM-DD format.",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Optional. New end date in YYYY-MM-DD format. Must be after start_date if both are provided.",
                        },
                        "frequency": {
                            "type": "string",
                            "description": "Optional. New payroll frequency (e.g., 'weekly', 'bi-weekly', 'monthly', 'semi-monthly').",
                        },
                    },
                    "required": ["cycle_id"],
                },
            },
        }
