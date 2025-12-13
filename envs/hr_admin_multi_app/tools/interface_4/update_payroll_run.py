import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdatePayrollRun(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cycle_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Update an existing payroll cycle/run.
        Only provided fields will be updated.
        """
        payroll_cycles = data.get("payroll_cycles", {})
        timestamp = "2025-12-12T12:00:00"
        
        # Validate required parameter
        if not cycle_id:
            return json.dumps({
                "success": False,
                "error": "cycle_id is required"
            })
        
        # Validate cycle exists
        if cycle_id not in payroll_cycles:
            return json.dumps({
                "success": False,
                "error": f"cycle_id '{cycle_id}' does not reference a valid payroll cycle"
            })
        
        cycle = payroll_cycles[cycle_id]
        
        # Check if at least one field is being updated
        update_fields = [start_date, end_date, frequency, status]
        if all(field is None for field in update_fields):
            return json.dumps({
                "success": False,
                "error": "At least one field must be provided to update"
            })
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["open", "closed"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Determine the final start_date and end_date values (use updated if provided, otherwise existing)
        final_start_date = start_date if start_date is not None else cycle.get("start_date")
        final_end_date = end_date if end_date is not None else cycle.get("end_date")
        
        # Validate that no other payroll cycle already exists with the same start_date and end_date
        # (unique constraint on (start_date, end_date))
        if start_date is not None or end_date is not None:
            for cid, c in payroll_cycles.items():
                if cid != cycle_id and c.get("start_date") == final_start_date and c.get("end_date") == final_end_date:
                    return json.dumps({
                        "success": False,
                        "error": f"A payroll cycle already exists with start_date '{final_start_date}' and end_date '{final_end_date}' (cycle_id: '{cid}')"
                    })
        
        # Update fields
        if start_date is not None:
            cycle["start_date"] = start_date
        if end_date is not None:
            cycle["end_date"] = end_date
        if frequency is not None:
            cycle["frequency"] = frequency
        if status is not None:
            cycle["status"] = status
        
        # Update timestamp
        cycle["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "payroll_cycle": cycle
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_payroll_run",
                "description": "Update an existing payroll cycle/run. Only provided fields will be updated. Validates unique constraint on (start_date, end_date).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cycle_id": {
                            "type": "string",
                            "description": "Cycle ID to update (required)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format (optional)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format (optional)"
                        },
                        "frequency": {
                            "type": "string",
                            "description": "Payroll frequency (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Cycle status: open, closed (optional)",
                            "enum": ["open", "closed"]
                        }
                    },
                    "required": ["cycle_id"]
                }
            }
        }
