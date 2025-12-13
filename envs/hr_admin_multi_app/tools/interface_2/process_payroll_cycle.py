import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ProcessPayrollCycle(Tool):
    """
    Process (create or update) a payroll cycle.
    Used to create new cycles, set cutoff dates, or update cycle status.
    Validates that payroll cycles do not have overlapping date periods.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        start_date: [str] = None,
        end_date: [str] = None,
        frequency: [str] = None,
        cycle_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Process a payroll cycle - create new or update existing cycle.
        
        Args:
            data: Dictionary containing payroll_cycles
            start_date: Start date in YYYY-MM-DD format (required for creation)
            end_date: End date in YYYY-MM-DD format (required for creation)
            frequency: Frequency of cycle (e.g., 'bi-weekly', 'monthly') (required for creation)
            cycle_id: Optional cycle ID to update existing cycle
            status: Optional status ('open', 'closed')
            
        Returns:
            JSON string with success status and cycle details
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
        
        # Validate status if provided
        valid_statuses = ["open", "closed"]
        if status and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                }
            )
        
        timestamp = "2025-12-12T12:00:00"
        
        # UPDATE MODE: If cycle_id is provided
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
            
            # Update fields if provided
            if start_date:
                # Validate date format
                try:
                    if len(start_date) != 10 or start_date[4] != "-" or start_date[7] != "-":
                        raise ValueError("Invalid date format")
                    year, month, day = start_date.split("-")
                    year_int, month_int, day_int = int(year), int(month), int(day)
                    if not (1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 1900):
                        raise ValueError("Invalid date values")
                except (ValueError, AttributeError):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid start_date format. Expected YYYY-MM-DD, got: '{start_date}'",
                        }
                    )
                cycle["start_date"] = start_date
            
            if end_date:
                # Validate date format
                try:
                    if len(end_date) != 10 or end_date[4] != "-" or end_date[7] != "-":
                        raise ValueError("Invalid date format")
                    year, month, day = end_date.split("-")
                    year_int, month_int, day_int = int(year), int(month), int(day)
                    if not (1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 1900):
                        raise ValueError("Invalid date values")
                except (ValueError, AttributeError):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid end_date format. Expected YYYY-MM-DD, got: '{end_date}'",
                        }
                    )
                cycle["end_date"] = end_date
            
            if frequency:
                cycle["frequency"] = frequency
            
            if status:
                cycle["status"] = status
            
            cycle["last_updated"] = timestamp
            
            # Check for overlapping cycles if dates were updated
            if start_date or end_date:
                current_start = cycle["start_date"]
                current_end = cycle["end_date"]
                
                # Validate date range
                if current_start >= current_end:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"start_date ('{current_start}') must be before end_date ('{current_end}')",
                        }
                    )
                
                # Check for overlapping periods with other cycles
                for other_id, other_cycle in payroll_cycles.items():
                    if other_id != cycle_id_str:
                        other_start = other_cycle.get("start_date")
                        other_end = other_cycle.get("end_date")
                        
                        # Two date ranges overlap if: (start1 <= end2) AND (start2 <= end1)
                        if other_start and other_end:
                            if current_start <= other_end and other_start <= current_end:
                                return json.dumps(
                                    {
                                        "success": False,
                                        "error": f"Payroll cycle dates overlap with existing cycle '{other_id}' ('{other_start}' to '{other_end}'). Cycles cannot have overlapping periods.",
                                    }
                                )
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Payroll cycle '{cycle_id_str}' has been updated successfully",
                    "cycle": cycle,
                    "action": "updated",
                }
            )
        
        # CREATE MODE: If cycle_id is not provided
        else:
            # Validate required fields for creation
            if not start_date:
                return json.dumps(
                    {"success": False, "error": "start_date is required for creating a new cycle"}
                )
            
            if not end_date:
                return json.dumps(
                    {"success": False, "error": "end_date is required for creating a new cycle"}
                )
            
            if not frequency:
                return json.dumps(
                    {"success": False, "error": "frequency is required for creating a new cycle"}
                )
            
            # Validate date formats
            try:
                if len(start_date) != 10 or start_date[4] != "-" or start_date[7] != "-":
                    raise ValueError("Invalid start_date format")
                year, month, day = start_date.split("-")
                year_int, month_int, day_int = int(year), int(month), int(day)
                if not (1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 1900):
                    raise ValueError("Invalid start_date values")
            except (ValueError, AttributeError):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid start_date format. Expected YYYY-MM-DD, got: '{start_date}'",
                    }
                )
            
            try:
                if len(end_date) != 10 or end_date[4] != "-" or end_date[7] != "-":
                    raise ValueError("Invalid end_date format")
                year, month, day = end_date.split("-")
                year_int, month_int, day_int = int(year), int(month), int(day)
                if not (1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 1900):
                    raise ValueError("Invalid end_date values")
            except (ValueError, AttributeError):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid end_date format. Expected YYYY-MM-DD, got: '{end_date}'",
                    }
                )
            
            # Validate date range
            if start_date >= end_date:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"start_date ('{start_date}') must be before end_date ('{end_date}')",
                    }
                )
            
            # Check for overlapping cycles
            for existing_cycle in payroll_cycles.values():
                existing_start = existing_cycle.get("start_date")
                existing_end = existing_cycle.get("end_date")
                
                # Two date ranges overlap if: (start1 <= end2) AND (start2 <= end1)
                if existing_start and existing_end:
                    if start_date <= existing_end and existing_start <= end_date:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Payroll cycle dates ('{start_date}' to '{end_date}') overlap with existing cycle '{existing_cycle.get('cycle_id')}' ('{existing_start}' to '{existing_end}'). Cycles cannot have overlapping periods.",
                            }
                        )
            
            # Generate new cycle ID
            def generate_cycle_id(cycles: Dict[str, Any]) -> str:
                if not cycles:
                    return "1"
                try:
                    max_id = max(int(k) for k in cycles.keys() if k.isdigit())
                    return str(max_id + 1)
                except ValueError:
                    return "1"
            
            new_cycle_id = generate_cycle_id(payroll_cycles)
            
            # Create new cycle
            new_cycle = {
                "cycle_id": new_cycle_id,
                "start_date": start_date,
                "end_date": end_date,
                "frequency": frequency,
                "status": status if status else "open",  # Default to 'open'
                "created_at": timestamp,
                "last_updated": timestamp,
            }
            
            payroll_cycles[new_cycle_id] = new_cycle
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Payroll cycle has been created successfully from '{start_date}' to '{end_date}'",
                    "cycle": new_cycle,
                    "action": "created",
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
                "name": "process_payroll_cycle",
                "description": (
                    "Process (create or update) a payroll cycle. "
                    "CREATE MODE: If cycle_id is not provided, creates a new payroll cycle. "
                    "Requires start_date, end_date, and frequency. "
                    "Validates that the cycle does not overlap with any existing cycles. "
                    "Payroll cycles cannot have overlapping date periods. "
                    "Default status is 'open'. "
                    "UPDATE MODE: If cycle_id is provided, updates the existing cycle. "
                    "Can update start_date, end_date, frequency, and/or status. "
                    "Also validates no overlap with other cycles when dates are updated. "
                    "Used to set cutoff dates or change cycle status (open → closed)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date of the cycle in YYYY-MM-DD format (required for creation)",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date of the cycle in YYYY-MM-DD format (required for creation)",
                        },
                        "frequency": {
                            "type": "string",
                            "description": "Frequency of the payroll cycle (e.g., 'bi-weekly', 'monthly', 'weekly') (required for creation)",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional: Cycle ID to update an existing cycle. If provided, enters UPDATE mode.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the cycle (optional, defaults to 'open' for new cycles). Valid values: 'open', 'closed'",
                            "enum": ["open", "closed"],
                        },
                    },
                    "required": ["start_date","end_date","frequency"],
                },
            },
        }

