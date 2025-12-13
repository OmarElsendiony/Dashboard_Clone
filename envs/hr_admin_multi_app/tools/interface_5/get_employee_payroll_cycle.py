import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetEmployeePayrollCycle(Tool):
    """
    Retrieve payroll cycle information based on status.
    - Returns payroll cycles filtered by status.
    - Does not require employee association.
    - Returns cycle details including dates, frequency, and status.
    - Returns all cycles if no status filter is provided.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cycle_status: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payroll_cycles": [...]} on success
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

        payroll_cycles_dict = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
                }
            )

        # Validate status if provided
        valid_statuses = ["open", "closed"]
        if cycle_status and cycle_status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{cycle_status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Retrieve payroll cycles based on status filter
        payroll_cycles = []

        for cycle_id, cycle in payroll_cycles_dict.items():
            if not isinstance(cycle, dict):
                continue

            cycle_data_status = cycle.get("status")

            # Filter by status if specified, otherwise include all
            if not cycle_status or cycle_data_status == cycle_status:
                cycle_copy = cycle.copy()
                payroll_cycles.append(cycle_copy)

        # Sort by start_date (most recent first) for better UX
        payroll_cycles.sort(key=lambda x: x.get("start_date", ""), reverse=True)

        return json.dumps(
            {
                "success": True,
                "payroll_cycles": payroll_cycles,
                "count": len(payroll_cycles),
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
                "name": "get_employee_payroll_cycle",
                "description": (
                    "Retrieve payroll cycle information based filter criteria. "
                    "Returns all payroll cycles that match the filters. "
                    "Can filter by cycle status (open, closed). "
                    "Returns cycle details including cycle_id, start_date, end_date, frequency, and status. "
                    "If no cycle_status is provided, returns all payroll cycles."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cycle_status": {
                            "type": "string",
                            "description": "Optional filter for cycle status. Accepted values: 'open', 'closed'. If not provided, returns all cycles.",
                        }
                    },
                    "required": [],
                },
            },
        }
