import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdatePayslipStatus(Tool):
    """
    Update the status of a payslip with automatic net pay recalculation.
    - Updates payslip status (draft, released, updated).
    - Automatically recalculates net pay using the formula:
      * Hourly Rate = Annual Base Salary / (26 weeks * 80 hours/week)
      * Gross Pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5)
      * Net Pay = Gross Pay + earnings - deductions
    - Validates payslip exists before updating.
    - Returns the updated payslip details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payslip_id: str,
        status: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payslip": {...}} on success
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

        payslips_dict = data.get("payslips", {})
        if not isinstance(payslips_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payslips container: expected dict at data['payslips']",
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

        payroll_earnings_dict = data.get("payroll_earnings", {})
        if not isinstance(payroll_earnings_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_earnings container: expected dict at data['payroll_earnings']",
                }
            )

        deductions_dict = data.get("deductions", {})
        if not isinstance(deductions_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid deductions container: expected dict at data['deductions']",
                }
            )

        # Validate payslip_id is provided
        if not payslip_id:
            return json.dumps({"success": False, "error": "payslip_id is required"})

        # Convert payslip_id to string for consistent comparison
        payslip_id_str = str(payslip_id)

        # Check if payslip exists
        if payslip_id_str not in payslips_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payslip with ID '{payslip_id_str}' not found",
                }
            )

        # Get the existing payslip
        payslip = payslips_dict[payslip_id_str]
        if not isinstance(payslip, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid payslip data for ID '{payslip_id_str}'",
                }
            )

        # At least status must be provided for update
        if not status:
            return json.dumps(
                {
                    "success": False,
                    "error": "status is required for update",
                }
            )

        # Validate status if provided
        valid_statuses = ["draft", "released", "updated"]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Get employee and cycle information from payslip
        employee_id_str = str(payslip.get("employee_id"))
        cycle_id_str = str(payslip.get("cycle_id"))

        # Check if employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        employee = employees_dict[employee_id_str]
        if not isinstance(employee, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid employee data for ID '{employee_id_str}'",
                }
            )

        # Get employee's base salary
        base_salary = employee.get("base_salary")
        if base_salary is None:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee '{employee_id_str}' does not have a base_salary defined",
                }
            )

        try:
            base_salary = float(base_salary)
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid base_salary value for employee '{employee_id_str}'",
                }
            )

        # Calculate hourly rate: Annual Base Salary / (26 weeks * 80 hours/week)
        hourly_rate = base_salary / (26 * 80)

        # Get payroll input for this employee and cycle
        hours_worked = 0
        overtime_hours = 0
        payroll_input_found = False

        for input_id, payroll_input in payroll_inputs_dict.items():
            if not isinstance(payroll_input, dict):
                continue
            
            if (str(payroll_input.get("employee_id")) == employee_id_str and 
                str(payroll_input.get("cycle_id")) == cycle_id_str):
                hours_worked = float(payroll_input.get("hours_worked", 0))
                overtime_hours = float(payroll_input.get("overtime_hours", 0))
                payroll_input_found = True
                break

        if not payroll_input_found:
            return json.dumps(
                {
                    "success": False,
                    "error": f"No payroll input found for employee '{employee_id_str}' in cycle '{cycle_id_str}'",
                }
            )

        # Calculate Gross Pay: (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5)
        gross_pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5)

        # Calculate total approved earnings for this employee
        total_earnings = 0
        for earning_id, earning in payroll_earnings_dict.items():
            if not isinstance(earning, dict):
                continue
            
            if (str(earning.get("employee_id")) == employee_id_str and 
                earning.get("status") == "approved"):
                total_earnings += float(earning.get("amount", 0))

        # Calculate total valid deductions for this employee and cycle
        total_deductions = 0
        for deduction_id, deduction in deductions_dict.items():
            if not isinstance(deduction, dict):
                continue
            
            if (str(deduction.get("employee_id")) == employee_id_str and 
                deduction.get("status") == "valid"):
                # Check if deduction is for this cycle or not linked to a specific cycle
                deduction_cycle_id = deduction.get("cycle_id")
                if deduction_cycle_id is None or str(deduction_cycle_id) == cycle_id_str:
                    # Check if deduction is active (not ended)
                    if deduction.get("is_active", True):
                        total_deductions += float(deduction.get("amount", 0))

        # Calculate Net Pay: Gross Pay + earnings - deductions
        net_pay_value = gross_pay + total_earnings - total_deductions

        # Ensure net pay is not negative
        if net_pay_value < 0:
            net_pay_value = 0

        # Update the payslip
        payslip["status"] = status
        payslip["net_pay_value"] = round(net_pay_value, 2)

        # Update timestamp
        payslip["last_updated"] = "2025-12-12T12:00:00"

        return json.dumps(
            {
                "success": True,
                "payslip": payslip,
                "message": f"Payslip '{payslip_id_str}' updated successfully",
                "calculation_details": {
                    "base_salary": base_salary,
                    "hourly_rate": round(hourly_rate, 2),
                    "hours_worked": hours_worked,
                    "overtime_hours": overtime_hours,
                    "gross_pay": round(gross_pay, 2),
                    "total_earnings": round(total_earnings, 2),
                    "total_deductions": round(total_deductions, 2),
                    "net_pay": round(net_pay_value, 2),
                }
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
                "name": "update_payslip_status",
                "description": (
                    "Update the status of a payslip with automatic net pay recalculation. "
                    "Recalculates net pay using: "
                    "Hourly Rate = Annual Base Salary / (26 weeks * 80 hours/week), "
                    "Gross Pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5), "
                    "Net Pay = Gross Pay + approved earnings - valid deductions. "
                    "Returns the updated payslip details with calculation breakdown."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payslip_id": {
                            "type": "string",
                            "description": "The ID of the payslip to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "New status for the payslip. Accepted values: 'draft', 'released', 'updated'.",
                        }
                    },
                    "required": ["payslip_id", "status"],
                },
            },
        }