import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class OpenPayrollPeriod(Tool):
    """
    Retrieve payroll cycles with flexible filtering options.
    Used to confirm open cycles, validate cycle periods, and check for overlapping cycles.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cycle_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        """
        Retrieve payroll cycle(s) with optional filtering.
        
        Args:
            data: Dictionary containing payroll_cycles
            cycle_id: Optional specific cycle ID to retrieve
            status: Optional status filter (e.g., 'open', 'approved', 'closed')
            start_date: Optional start date filter in YYYY-MM-DD format
            end_date: Optional end date filter in YYYY-MM-DD format
            
        Returns:
            JSON string with success status and cycle(s) information
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        payroll_cycles = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
                }
            )
        
        # If cycle_id is provided, return that specific cycle
        if cycle_id:
            cycle_id_str = str(cycle_id)
            
            if cycle_id_str not in payroll_cycles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                    }
                )
            
            cycle = payroll_cycles[cycle_id_str]
            return json.dumps(
                {
                    "success": True,
                    "cycle": cycle,
                }
            )
        
        # Filter cycles based on provided parameters
        filtered_cycles = []
        
        for cycle in payroll_cycles.values():
            # Apply status filter (default to 'open' if no filters provided)
            if status is None and start_date is None and end_date is None:
                # Default behavior: return only open cycles
                if cycle.get("status") != "open":
                    continue
            else:
                # If status filter is provided, apply it
                if status is not None and cycle.get("status") != status:
                    continue
            
            # Apply start_date filter (check for overlapping or matching periods)
            if start_date is not None:
                cycle_start = cycle.get("start_date")
                cycle_end = cycle.get("end_date")
                
                # Check if the provided start_date overlaps with or matches the cycle period
                if cycle_start and cycle_end:
                    # If checking for overlapping periods: start_date falls within cycle period
                    # or if exact match is needed
                    if not (cycle_start <= start_date <= cycle_end or cycle_start == start_date):
                        # If start_date doesn't overlap, skip unless we're checking for period overlap
                        # For validation purposes, we check if ranges overlap
                        if end_date:
                            # Check if date ranges overlap: (start1 <= end2) and (start2 <= end1)
                            if not (cycle_start <= end_date and start_date <= cycle_end):
                                continue
                        else:
                            # Just checking if start_date falls within cycle
                            if not (cycle_start <= start_date <= cycle_end):
                                continue
            
            # Apply end_date filter
            if end_date is not None and start_date is None:
                cycle_start = cycle.get("start_date")
                cycle_end = cycle.get("end_date")
                
                if cycle_end and cycle_start:
                    # Check if end_date falls within cycle period
                    if not (cycle_start <= end_date <= cycle_end):
                        continue
            
            filtered_cycles.append(cycle)
        
        if not filtered_cycles:
            filter_desc = []
            if status:
                filter_desc.append(f"status='{status}'")
            if start_date:
                filter_desc.append(f"start_date='{start_date}'")
            if end_date:
                filter_desc.append(f"end_date='{end_date}'")
            
            filter_str = " with " + ", ".join(filter_desc) if filter_desc else ""
            message = f"No payroll cycles found{filter_str}" if filter_desc else "No open payroll cycles found"
            
            return json.dumps(
                {
                    "success": True,
                    "count": 0,
                    "cycles": [],
                    "message": message,
                }
            )
        
        return json.dumps(
            {
                "success": True,
                "count": len(filtered_cycles),
                "cycles": filtered_cycles,
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
                "name": "open_payroll_period",
                "description": (
                    "Retrieve payroll cycle(s) information with flexible filtering options. "
                    "If cycle_id is provided, returns that specific cycle. "
                    "Otherwise, filters cycles by status, start_date, and/or end_date. "
                    "If no filters are provided, defaults to returning all cycles with 'open' status. "
                    "Used to confirm open cycles are available, validate cycle periods, and check for overlapping cycles. "
                    "Payroll cycle statuses can be: 'open', 'approved', or 'closed'. "
                    "Date filters can be used to find cycles that overlap with a specific time period."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional: Specific payroll cycle ID to retrieve. If provided, other filters are ignored.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional: Filter cycles by status ('open', 'approved', or 'closed'). If omitted with no other filters, defaults to 'open'.",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Optional: Filter cycles by start date in YYYY-MM-DD format. When combined with end_date, finds cycles that overlap with the specified period.",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Optional: Filter cycles by end date in YYYY-MM-DD format. When combined with start_date, finds cycles that overlap with the specified period.",
                        },
                    },
                    "required": [],
                },
            },
        }

