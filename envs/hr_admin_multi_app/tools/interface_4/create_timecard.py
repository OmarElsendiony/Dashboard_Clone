import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateTimecard(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        hours_worked: float,
        overtime_hours: float = 0.0,
        status: str = "pending",
        payroll_variance_percent: Optional[float] = None,
        issue_field: Optional[str] = None
    ) -> str:
        """
        Create a new timecard (payroll input) record.
        """
        payroll_inputs = data.get("payroll_inputs", {})
        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required fields
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        if not cycle_id:
            return json.dumps({
                "success": False,
                "error": "cycle_id is required"
            })
        
        if hours_worked is None:
            return json.dumps({
                "success": False,
                "error": "hours_worked is required"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        # Validate cycle exists
        if cycle_id not in payroll_cycles:
            return json.dumps({
                "success": False,
                "error": f"cycle_id '{cycle_id}' does not reference a valid payroll cycle"
            })
        
        # Validate status
        valid_statuses = ["pending", "approved", "review"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Generate new input_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_input_id = generate_id(payroll_inputs)
        
        # Create new payroll input record
        new_timecard = {
            "input_id": new_input_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "hours_worked": str(hours_worked),
            "overtime_hours": str(overtime_hours),
            "payroll_variance_percent": str(payroll_variance_percent) if payroll_variance_percent is not None else None,
            "status": status,
            "issue_field": issue_field,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        payroll_inputs[new_input_id] = new_timecard
        
        return json.dumps({
            "success": True,
            "timecard": new_timecard
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_timecard",
                "description": "Create a new timecard (payroll input) record. Validates employee and cycle exist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Payroll cycle ID (required)"
                        },
                        "hours_worked": {
                            "type": "number",
                            "description": "Hours worked (required)"
                        },
                        "overtime_hours": {
                            "type": "number",
                            "description": "Overtime hours (optional, default: 0.0)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Timecard status: pending, approved, review (optional, default: 'pending')",
                            "enum": ["pending", "approved", "review"]
                        },
                        "payroll_variance_percent": {
                            "type": "number",
                            "description": "Payroll variance percentage (optional)"
                        },
                        "issue_field": {
                            "type": "string",
                            "description": "Issue field description (optional)"
                        }
                    },
                    "required": ["employee_id", "cycle_id", "hours_worked"]
                }
            }
        }
