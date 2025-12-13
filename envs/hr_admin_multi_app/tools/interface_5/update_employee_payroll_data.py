import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateEmployeePayrollData(Tool):
    """
    Update existing payroll input data for an employee.
    - Updates payroll input with new hours worked and/or overtime hours.
    - Calculates payroll variance percentage based on gross pay changes.
    - Flags issues if variance exceeds 1%.
    - Validates payroll input exists before updating.
    - Returns the updated payroll input details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        input_id: str,
        hours_worked: Optional[float] = None,
        overtime_hours: Optional[float] = None,
        input_status: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payroll_input": {...}} on success
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

        employees_dict = data.get("employees", {})
        if not isinstance(employees_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )

        payroll_inputs_dict = data.get("payroll_inputs", {})
        if not isinstance(payroll_inputs_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_inputs container: expected dict at data['payroll_inputs']",
                }
            )

        # Validate input_status if provided
        if input_status:
            valid_payroll_statuses = {"pending", "approved", "cancelled", "locked"}
            if input_status not in valid_payroll_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid input_status '{input_status}'. Must be one of {valid_payroll_statuses}",
                    }
                )

        # Validate input_id is provided
        if not input_id:
            return json.dumps({"success": False, "error": "input_id is required"})

        # Convert input_id to string for consistent comparison
        input_id_str = str(input_id)

        # Check if payroll input exists
        if input_id_str not in payroll_inputs_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll input with ID '{input_id_str}' not found",
                }
            )

        # Get existing payroll input
        payroll_input = payroll_inputs_dict[input_id_str]
        if not isinstance(payroll_input, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid payroll input data for ID '{input_id_str}'",
                }
            )

        # At least one field must be provided for update
        if not hours_worked and not overtime_hours and not input_status:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field (hours_worked, overtime_hours, or input_status) must be provided for update",
                }
            )

        # Validate numeric values if provided
        try:
            if hours_worked:
                hours_worked = float(hours_worked)
                if hours_worked < 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "hours_worked cannot be negative",
                        }
                    )

            if overtime_hours:
                overtime_hours = float(overtime_hours)
                if overtime_hours < 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "overtime_hours cannot be negative",
                        }
                    )
        except (ValueError, TypeError) as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid numeric value: {str(e)}",
                }
            )

        # Get employee to calculate hourly rate
        employee_id = str(payroll_input.get("employee_id"))
        if employee_id not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id}' not found",
                }
            )

        employee = employees_dict[employee_id]
        base_salary = employee.get("base_salary")
        if not base_salary:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee '{employee_id}' does not have a base_salary defined",
                }
            )

        try:
            base_salary = float(base_salary)
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid base_salary value for employee '{employee_id}'",
                }
            )

        # Calculate hourly rate: Annual Base Salary / (26 weeks × 80 hours/week)
        hourly_rate = base_salary / (26 * 80)

        # Get previous values
        previous_hours = float(payroll_input.get("hours_worked", 0))
        previous_overtime = float(payroll_input.get("overtime_hours", 0))

        # Determine new values
        new_hours_worked = hours_worked if hours_worked is not None else previous_hours
        new_overtime_hours = (
            overtime_hours if overtime_hours is not None else previous_overtime
        )

        # Calculate previous and current gross pay
        # Gross Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5)
        previous_gross_pay = (previous_hours * hourly_rate) + (
            previous_overtime * hourly_rate * 1.5
        )
        current_gross_pay = (new_hours_worked * hourly_rate) + (
            new_overtime_hours * hourly_rate * 1.5
        )

        # Calculate variance if there's a change in hours
        payroll_variance_percent = None
        status = (
            input_status if input_status else payroll_input.get("status", "pending")
        )
        issue_field = None

        if (hours_worked or overtime_hours) and previous_gross_pay > 0:
            # Variance = ((previous_gross_pay - current_gross_pay) / previous_gross_pay) × 100
            variance = (
                (previous_gross_pay - current_gross_pay) / previous_gross_pay
            ) * 100
            payroll_variance_percent = round(variance, 2)

            # Flag if variance exceeds 1%
            if abs(payroll_variance_percent) > 1.0:
                status = "review"
                issue_field = f"variance exceeds 1% ({payroll_variance_percent}%)"
            else:
                # Reset to provided status or keep current if variance is within limits
                if not input_status:
                    status = "pending"
                issue_field = None

        # Update the payroll input
        if hours_worked:
            payroll_input["hours_worked"] = new_hours_worked

        if overtime_hours:
            payroll_input["overtime_hours"] = new_overtime_hours

        if hours_worked or overtime_hours:
            payroll_input["payroll_variance_percent"] = payroll_variance_percent
            payroll_input["status"] = status
            payroll_input["issue_field"] = issue_field
        elif input_status:
            # Only status update without hours changes
            payroll_input["status"] = status

        # Update timestamp
        payroll_input["last_updated"] = "2025-11-16T23:59:00"

        return json.dumps(
            {
                "success": True,
                "payroll_input": payroll_input,
                "message": f"Payroll input '{input_id_str}' updated successfully",
                "variance_calculated": payroll_variance_percent is not None,
                "calculation_details": (
                    {
                        "hourly_rate": round(hourly_rate, 2),
                        "previous_gross_pay": round(previous_gross_pay, 2),
                        "current_gross_pay": round(current_gross_pay, 2),
                        "variance_percent": payroll_variance_percent,
                    }
                    if payroll_variance_percent is not None
                    else None
                ),
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
                "name": "update_employee_payroll_data",
                "description": (
                    "Update existing payroll input data for an employee. "
                    "Updates hours worked, overtime hours, and/or status. "
                    "Calculates payroll variance percentage based on gross pay changes: "
                    "Gross Pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5), "
                    "Variance = ((previous_gross_pay - current_gross_pay) / previous_gross_pay) * 100. "
                    "Flags issues if variance exceeds 1% "
                    "Returns the updated payroll input details with calculation breakdown."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_id": {
                            "type": "string",
                            "description": "The ID of the payroll input to update.",
                        },
                        "hours_worked": {
                            "type": "number",
                            "description": "Optional. New total regular hours worked. Must be non-negative. Triggers variance calculation.",
                        },
                        "overtime_hours": {
                            "type": "number",
                            "description": "Optional. New overtime hours worked. Must be non-negative. Triggers variance calculation.",
                        },
                        "input_status": {
                            "type": "string",
                            "description": "Optional. New status for the payroll input. Must be one of 'pending', 'approved', 'cancelled', or 'locked'.",
                        },
                    },
                    "required": ["input_id"],
                },
            },
        }
