import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class GetTimecards(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: Optional[str] = None,
        cycle_id: Optional[str] = None
    ) -> str:
        """
        Get timecard(s) (payroll input) based on filter criteria.
        Returns all timecards that match the specified filters.
        """
        payroll_inputs = data.get("payroll_inputs", {})
        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        results = []
        
        # Validate employee_id if provided
        if employee_id:
            if employee_id not in employees:
                return json.dumps({
                    "success": False,
                    "error": f"employee_id '{employee_id}' does not reference a valid employee",
                    "count": 0,
                    "timecards": []
                })
        
        # Validate cycle_id if provided
        if cycle_id:
            if cycle_id not in payroll_cycles:
                return json.dumps({
                    "success": False,
                    "error": f"cycle_id '{cycle_id}' does not reference a valid payroll cycle",
                    "count": 0,
                    "timecards": []
                })
        
        # Filter timecards
        for input_id, timecard in payroll_inputs.items():
            match = True
            
            if employee_id and timecard.get("employee_id") != employee_id:
                match = False
            if cycle_id and timecard.get("cycle_id") != cycle_id:
                match = False
            
            if match:
                # Create a copy of the timecard to avoid modifying the original
                timecard_copy = timecard.copy()
                results.append(timecard_copy)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "timecards": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_timecards",
                "description": "Get timecard(s) (payroll input) based on filter criteria. Returns all timecards that match the specified filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Filter by employee ID (optional)"
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Filter by payroll cycle ID (optional)"
                        }
                    },
                    "required": []
                }
            }
        }
