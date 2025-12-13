import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreatePayrollRun(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        start_date: str,
        end_date: str,
        frequency: str,
        status: str = 'open'
    ) -> str:
        """
        Create a new payroll cycle/run.
        """
        payroll_cycles = data.get("payroll_cycles", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required fields
        if not start_date:
            return json.dumps({
                "success": False,
                "error": "start_date is required"
            })
        
        if not end_date:
            return json.dumps({
                "success": False,
                "error": "end_date is required"
            })
        
        if not frequency:
            return json.dumps({
                "success": False,
                "error": "frequency is required"
            })
        
        # Validate status
        valid_statuses = ["open", "closed"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Validate that no payroll cycle already exists with the same start_date and end_date
        # (unique constraint on (start_date, end_date))
        for cycle_id, cycle in payroll_cycles.items():
            if cycle.get("start_date") == start_date and cycle.get("end_date") == end_date:
                return json.dumps({
                    "success": False,
                    "error": f"A payroll cycle already exists with start_date '{start_date}' and end_date '{end_date}' (cycle_id: '{cycle_id}')"
                })
        
        # Generate new cycle_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_cycle_id = generate_id(payroll_cycles)
        
        # Create new payroll cycle record
        new_cycle = {
            "cycle_id": new_cycle_id,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        payroll_cycles[new_cycle_id] = new_cycle
        
        return json.dumps({
            "success": True,
            "payroll_cycle": new_cycle
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_payroll_run",
                "description": "Create a new payroll cycle/run. Validates that no cycle exists with the same start_date and end_date combination.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format (required)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format (required)"
                        },
                        "frequency": {
                            "type": "string",
                            "description": "Payroll frequency (required)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Cycle status: open, closed (optional, default: 'open')",
                            "enum": ["open", "closed"]
                        }
                    },
                    "required": ["start_date", "end_date", "frequency"]
                }
            }
        }
