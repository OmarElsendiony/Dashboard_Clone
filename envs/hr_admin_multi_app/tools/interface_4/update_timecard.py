import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateTimecard(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        input_id: str,
        hours_worked: Optional[float] = None,
        overtime_hours: Optional[float] = None,
        status: Optional[str] = None,
        payroll_variance_percent: Optional[float] = None,
        issue_field: Optional[str] = None
    ) -> str:
        """
        Update an existing timecard (payroll input) record.
        Only provided fields will be updated.
        """
        payroll_inputs = data.get("payroll_inputs", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required parameter
        if not input_id:
            return json.dumps({
                "success": False,
                "error": "input_id is required"
            })
        
        # Validate timecard exists
        if input_id not in payroll_inputs:
            return json.dumps({
                "success": False,
                "error": f"input_id '{input_id}' does not reference a valid timecard"
            })
        
        timecard = payroll_inputs[input_id]
        
        # Check if at least one field is being updated
        update_fields = [hours_worked, overtime_hours, status, payroll_variance_percent, issue_field]
        if all(field is None for field in update_fields):
            return json.dumps({
                "success": False,
                "error": "At least one field must be provided to update"
            })
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["pending", "approved", "review"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Update fields
        if hours_worked is not None:
            timecard["hours_worked"] = str(hours_worked)
        if overtime_hours is not None:
            timecard["overtime_hours"] = str(overtime_hours)
        if status is not None:
            timecard["status"] = status
        if payroll_variance_percent is not None:
            timecard["payroll_variance_percent"] = str(payroll_variance_percent)
        if issue_field is not None:
            timecard["issue_field"] = issue_field
        
        # Update timestamp
        timecard["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "timecard": timecard
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_timecard",
                "description": "Update an existing timecard (payroll input) record. Only provided fields will be updated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_id": {
                            "type": "string",
                            "description": "Timecard input ID to update (required)"
                        },
                        "hours_worked": {
                            "type": "number",
                            "description": "Hours worked (optional)"
                        },
                        "overtime_hours": {
                            "type": "number",
                            "description": "Overtime hours (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Timecard status: pending, approved, review (optional)",
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
                    "required": ["input_id"]
                }
            }
        }
