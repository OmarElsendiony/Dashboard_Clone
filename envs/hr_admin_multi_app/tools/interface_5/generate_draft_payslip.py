import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GenerateDraftPayslip(Tool):
    """
    Generate a draft payslip for an employee.
    - Creates a new payslip for an employee in a specific payroll cycle.
    - Calculates net pay value based on base salary, earnings, and deductions.
    - Validates employee exists, cycle exists and is approved.
    - Ensures no duplicate payslip exists for the same employee-cycle combination.
    - Sets initial status as 'draft'.
    - Returns the created payslip details or an error.
    """

    @staticmethod
    def invoke(data: Dict[str, Any], employee_id: str, cycle_id: str) -> str:
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

        payroll_cycles_dict = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
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

        # Validate required parameters
        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})

        if not cycle_id:
            return json.dumps({"success": False, "error": "cycle_id is required"})

        # Convert IDs to strings for consistent comparison
        employee_id_str = str(employee_id)
        cycle_id_str = str(cycle_id)

        # Check if employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        # Check if cycle exists
        if cycle_id_str not in payroll_cycles_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                }
            )

        # Validate cycle status is 'approved' (per SOP 13)
        cycle = payroll_cycles_dict[cycle_id_str]
        if not isinstance(cycle, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid cycle data for ID '{cycle_id_str}'",
                }
            )

        if cycle.get("status") != "approved":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle '{cycle_id_str}' must have status 'approved' to generate payslip. Current status: {cycle.get('status')}",
                }
            )

        # Check if payslip already exists for this employee-cycle combination (per schema unique constraint)
        for payslip_id, payslip in payslips_dict.items():
            if not isinstance(payslip, dict):
                continue

            if (
                str(payslip.get("employee_id")) == employee_id_str
                and str(payslip.get("cycle_id")) == cycle_id_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payslip already exists for employee '{employee_id_str}' in cycle '{cycle_id_str}' (payslip_id: {payslip_id})",
                    }
                )

        # Get employee's base salary
        base_salary = employees_dict.get("base_salary")
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

        # Calculate hourly rate: Annual Base Salary / (26 weeks × 80 hours/week)
        hourly_rate = base_salary / (26 * 80)

        # Get payroll input for this employee and cycle
        hours_worked = 0
        overtime_hours = 0
        payroll_input_found = False

        for input_id, payroll_input in payroll_inputs_dict.items():
            if not isinstance(payroll_input, dict):
                continue

            if (
                str(payroll_input.get("employee_id")) == employee_id_str
                and str(payroll_input.get("cycle_id")) == cycle_id_str
            ):
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

        # Calculate Gross Pay: (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5)
        gross_pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5)

        # Calculate total approved earnings for this employee
        total_earnings = 0
        for earning_id, earning in payroll_earnings_dict.items():
            if not isinstance(earning, dict):
                continue

            if (
                str(earning.get("employee_id")) == employee_id_str
                and earning.get("status") == "approved"
            ):
                total_earnings += float(earning.get("amount", 0))

        # Calculate total valid deductions for this employee and cycle
        total_deductions = 0
        for deduction_id, deduction in deductions_dict.items():
            if not isinstance(deduction, dict):
                continue

            if (
                str(deduction.get("employee_id")) == employee_id_str
                and deduction.get("status") == "valid"
            ):
                # Check if deduction is for this cycle or not linked to a specific cycle
                deduction_cycle_id = deduction.get("cycle_id")
                if (
                    deduction_cycle_id is None
                    or str(deduction_cycle_id) == cycle_id_str
                ):
                    # Check if deduction is active (not ended)
                    if deduction.get("is_active", True):
                        total_deductions += float(deduction.get("amount", 0))

        # Calculate Net Pay: Gross Pay + earnings - deductions
        net_pay_value = gross_pay + total_earnings - total_deductions

        # Ensure net pay is not negative
        if net_pay_value < 0:
            net_pay_value = 0

        # Generate new payslip_id
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_payslip_id = generate_id(payslips_dict)

        current_timestamp = "2025-12-12T12:00:00"

        # Create new payslip
        new_payslip = {
            "payslip_id": new_payslip_id,
            "employee_id": employee_id_str,
            "cycle_id": cycle_id_str,
            "net_pay_value": net_pay_value,
            "status": "draft",
            "created_at": current_timestamp,
            "last_updated": current_timestamp,
        }

        # Add to data
        payslips_dict[new_payslip_id] = new_payslip

        return json.dumps(
            {
                "success": True,
                "payslip": new_payslip,
                "message": f"Draft payslip created successfully with ID: {new_payslip_id}",
                "calculation_details": {
                    "base_salary": base_salary,
                    "hourly_rate": round(hourly_rate, 2),
                    "hours_worked": hours_worked,
                    "overtime_hours": overtime_hours,
                    "gross_pay": round(gross_pay, 2),
                    "total_earnings": round(total_earnings, 2),
                    "total_deductions": round(total_deductions, 2),
                    "net_pay": round(net_pay_value, 2),
                },
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
                "name": "generate_draft_payslip",
                "description": (
                    "Generate a draft payslip for an employee in a specific payroll cycle with automatic net pay calculation. "
                    "Calculates net pay using: "
                    "Hourly Rate = Annual Base Salary / (52 weeks * 80 hours/week), "
                    "Gross Pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5), "
                    "Net Pay = Gross Pay + approved earnings - valid deductions. "
                    "Validates that employee exists, cycle exists and has 'approved' status, "
                    "and payroll input exists for the employee-cycle. "
                    "Ensures no duplicate payslip exists for the same employee-cycle combination. "
                    "Sets initial status as 'draft'. "
                    "Returns the created payslip details with calculation breakdown."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee to generate payslip for.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "The ID of the payroll cycle.",
                        },
                    },
                    "required": ["employee_id", "cycle_id"],
                },
            },
        }
