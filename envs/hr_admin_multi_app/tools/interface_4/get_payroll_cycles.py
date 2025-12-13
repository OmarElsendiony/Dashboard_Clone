import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class GetPayrollCycles(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """
        Get payroll cycle(s) based on filter criteria.
        Returns all payroll cycles that match the specified filters.
        """
        payroll_cycles = data.get("payroll_cycles", {})
        results = []
        
        # Validate status if provided
        if status:
            valid_statuses = ["open", "closed"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    "count": 0,
                    "payroll_cycles": []
                })
        
        # Filter payroll cycles
        for cycle_id, cycle in payroll_cycles.items():
            match = True
            
            if status and cycle.get("status") != status:
                match = False
            if start_date and cycle.get("start_date") != start_date:
                match = False
            if end_date and cycle.get("end_date") != end_date:
                match = False
            
            if match:
                # Create a copy of the cycle to avoid modifying the original
                cycle_copy = cycle.copy()
                results.append(cycle_copy)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "payroll_cycles": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_payroll_cycles",
                "description": "Get payroll cycle(s) based on filter criteria. Returns all payroll cycles that match the specified filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by status: open, closed (optional)",
                            "enum": ["open", "closed"]
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Filter by start date in YYYY-MM-DD format (optional)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Filter by end date in YYYY-MM-DD format (optional)"
                        }
                    },
                    "required": []
                }
            }
        }
