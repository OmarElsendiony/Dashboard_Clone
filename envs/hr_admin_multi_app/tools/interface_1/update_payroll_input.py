import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdatePayrollInput(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        input_id: str,
        hours_worked: Optional[float] = None,
        overtime_hours: Optional[float] = None,
        allowance_amount: Optional[float] = None,
        payroll_variance_percent: Optional[float] = None,
        status: Optional[str] = None,
        issue_field: Optional[str] = None,
    ) -> str:
        """
        Updates an existing payroll input record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not input_id:
            return json.dumps({"error": "input_id is required"})

        # Convert IDs to strings for consistent comparison
        input_id = str(input_id)

        payroll_inputs = data.get("payroll_inputs", {})
        if input_id not in payroll_inputs:
            return json.dumps(
                {"error": f"Payroll input with ID '{input_id}' not found"}
            )

        if (
            hours_worked is None
            and overtime_hours is None
            and allowance_amount is None
            and payroll_variance_percent is None
            and status is None
            and issue_field is None
        ):
            return json.dumps(
                {"error": "No fields provided to update. Provide at least one field"}
            )

        if hours_worked is not None and hours_worked < 0:
            return json.dumps(
                {"error": "hours_worked must be a non-negative number when provided"}
            )
        if overtime_hours is not None and overtime_hours < 0:
            return json.dumps(
                {"error": "overtime_hours must be a non-negative number when provided"}
            )
        if allowance_amount is not None and allowance_amount < 0:
            return json.dumps(
                {"error": "allowance_amount must be a non-negative number when provided"}
            )

        allowed_statuses = ["pending", "review"]
        if status is not None and status not in allowed_statuses:
            return json.dumps(
                {
                    "error": "Invalid status. Allowed values: 'pending', 'review'"
                }
            )

        current_input = payroll_inputs[input_id]

        # SOP 9, Step 2: Calculate variance if key fields are being updated
        old_hours = current_input.get("hours_worked", 0)
        old_overtime = current_input.get("overtime_hours", 0)
        old_allowance = current_input.get("allowance_amount", 0)
        
        new_hours = hours_worked if hours_worked is not None else old_hours
        new_overtime = overtime_hours if overtime_hours is not None else old_overtime
        new_allowance = allowance_amount if allowance_amount is not None else old_allowance
        
        # Calculate total input value (as a proxy for payroll total)
        old_total = old_hours + old_overtime + old_allowance
        new_total = new_hours + new_overtime + new_allowance
        
        # Calculate variance percentage if there's a change in values
        calculated_variance = None
        if (hours_worked is not None or overtime_hours is not None or allowance_amount is not None):
            if old_total > 0:
                calculated_variance = abs((new_total - old_total) / old_total) * 100
            elif new_total > 0:
                calculated_variance = 100.0  # If old was 0 and new is not, that's 100% variance
        
        # Auto-enforce variance rule: if variance exceeds 1%, set status to "review"
        auto_status = None
        auto_issue_field = None
        if calculated_variance is not None and calculated_variance > 1.0:
            auto_status = "review"
            auto_issue_field = "variance exceeds 1%"
            # Store the calculated variance
            current_input["payroll_variance_percent"] = calculated_variance

        # Apply updates
        if hours_worked is not None:
            current_input["hours_worked"] = hours_worked
        if overtime_hours is not None:
            current_input["overtime_hours"] = overtime_hours
        if allowance_amount is not None:
            current_input["allowance_amount"] = allowance_amount
        if payroll_variance_percent is not None:
            current_input["payroll_variance_percent"] = payroll_variance_percent
        
        # Apply auto-enforced status/issue_field or user-provided values
        if auto_status is not None:
            current_input["status"] = auto_status
        elif status is not None:
            current_input["status"] = status
        
        if auto_issue_field is not None:
            current_input["issue_field"] = auto_issue_field
        elif issue_field is not None:
            current_input["issue_field"] = issue_field

        timestamp = "2025-11-22T12:00:00"
        current_input["last_updated"] = timestamp

        return json.dumps(current_input)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_payroll_input",
                "description": (
                    "Updates an existing payroll input record for an employee. "
                    "This tool is used to adjust hours, allowances, or to flag the record for review "
                    "with variance and issue details. "
                    "Per SOP 9, when hours_worked, overtime_hours, or allowance_amount are updated, "
                    "the tool automatically calculates the payroll variance percentage. If the variance exceeds 1%, "
                    "the status is automatically set to 'review' and the issue_field is set to 'variance exceeds 1%' "
                    "for internal verification."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_id": {
                            "type": "string",
                            "description": "ID of the payroll input record to update (required).",
                        },
                        "hours_worked": {
                            "type": "number",
                            "description": (
                                "Updated number of regular hours worked (optional). "
                                "Must be a non-negative number."
                            ),
                        },
                        "overtime_hours": {
                            "type": "number",
                            "description": (
                                "Updated number of overtime hours worked (optional). "
                                "Must be a non-negative number."
                            ),
                        },
                        "allowance_amount": {
                            "type": "number",
                            "description": (
                                "Updated allowance amount for this input (optional). "
                                "Must be a non-negative number."
                            ),
                        },
                        "payroll_variance_percent": {
                            "type": "number",
                            "description": (
                                "Updated payroll variance percentage for this input (optional). "
                                "Used to track variances compared to previous periods."
                            ),
                        },
                        "status": {
                            "type": "string",
                            "description": (
                                "Updated status of the payroll input (optional). "
                                "Allowed values: 'pending', 'review'."
                            ),
                        },
                        "issue_field": {
                            "type": "string",
                            "description": (
                                "Text describing any issue associated with this input (for example: "
                                "'variance exceeds 1%'). Optional."
                            ),
                        },
                    },
                    "required": ["input_id"],
                },
            },
        }
