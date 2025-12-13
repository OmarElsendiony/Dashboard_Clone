import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class InitiateEmployeePayment(Tool):
    """
    Initiate a payment for an employee.
    - Creates a new payment record linked to a payslip.
    - Records payment method and amount.
    - For final settlements, automatically calculates amount including asset charges.
    - For regular payments, uses provided amount.
    - Validates employee exists, payslip exists and has 'draft' status.
    - Sets initial payment status as 'pending'.
    - Returns the created payment details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        source_payslip_id: str,
        payment_method: str,
        is_final_settlement: bool = False,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payment": {...}} on success
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

        payments_dict = data.get("payments", {})
        if not isinstance(payments_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payments container: expected dict at data['payments']",
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

        employee_assets_dict = data.get("employee_assets", {})
        if not isinstance(employee_assets_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employee_assets container: expected dict at data['employee_assets']",
                }
            )

        # Validate required parameters
        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})

        if not source_payslip_id:
            return json.dumps(
                {"success": False, "error": "source_payslip_id is required"}
            )

        if not payment_method:
            return json.dumps({"success": False, "error": "payment_method is required"})

        # Convert IDs to strings for consistent comparison
        employee_id_str = str(employee_id)
        source_payslip_id_str = str(source_payslip_id)

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

        # Check if payslip exists
        if source_payslip_id_str not in payslips_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payslip with ID '{source_payslip_id_str}' not found",
                }
            )

        # Validate payslip status is 'draft' (per SOP 15)
        payslip = payslips_dict[source_payslip_id_str]
        if not isinstance(payslip, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid payslip data for ID '{source_payslip_id_str}'",
                }
            )

        if payslip.get("status") != "draft":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payslip '{source_payslip_id_str}' must have status 'draft' to initiate payment. Current status: {payslip.get('status')}",
                }
            )

        # Validate payment_method
        valid_payment_methods = ["Bank Transfer", "Check"]
        if payment_method not in valid_payment_methods:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid payment_method '{payment_method}'. Must be one of: {', '.join(valid_payment_methods)}",
                }
            )

        # Calculate amount if final settlement, otherwise get from payslip
        calculation_details = None
        if is_final_settlement:
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
            cycle_id_str = str(payslip.get("cycle_id"))
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
            gross_pay = (hours_worked * hourly_rate) + (
                overtime_hours * hourly_rate * 1.5
            )

            # Calculate total approved earnings for this employee
            total_payroll_earnings = 0
            for earning_id, earning in payroll_earnings_dict.items():
                if not isinstance(earning, dict):
                    continue

                if (
                    str(earning.get("employee_id")) == employee_id_str
                    and earning.get("status") == "approved"
                ):
                    total_payroll_earnings += float(earning.get("amount", 0))

            # Calculate Total Earning: Gross Pay + payroll_earning
            total_earning = gross_pay + total_payroll_earnings

            # Calculate total valid deductions for this employee
            total_deductions = 0
            for deduction_id, deduction in deductions_dict.items():
                if not isinstance(deduction, dict):
                    continue

                if (
                    str(deduction.get("employee_id")) == employee_id_str
                    and deduction.get("status") == "valid"
                ):
                    # Check if deduction is active (not ended)
                    if deduction.get("is_active", True):
                        total_deductions += float(deduction.get("amount", 0))

            # Calculate Asset Charges: (N_missing * 500) + (N_damaged * 250)
            n_missing = 0
            n_damaged = 0
            for asset_id, asset in employee_assets_dict.items():
                if not isinstance(asset, dict):
                    continue

                if str(asset.get("employee_id")) == employee_id_str:
                    asset_status = asset.get("status")
                    if asset_status == "missing":
                        n_missing += 1
                    elif asset_status == "damaged":
                        n_damaged += 1

            asset_charges = (n_missing * 500) + (n_damaged * 250)

            # Calculate Amount: Total Earning - deductions - Asset Charges
            amount = total_earning - total_deductions - asset_charges

            # Ensure amount is not negative
            if amount < 0:
                amount = 0

            calculation_details = {
                "base_salary": base_salary,
                "hourly_rate": round(hourly_rate, 2),
                "hours_worked": hours_worked,
                "overtime_hours": overtime_hours,
                "gross_pay": round(gross_pay, 2),
                "total_payroll_earnings": round(total_payroll_earnings, 2),
                "total_earning": round(total_earning, 2),
                "total_deductions": round(total_deductions, 2),
                "asset_charges": {
                    "missing_count": n_missing,
                    "damaged_count": n_damaged,
                    "total_charges": asset_charges,
                },
                "final_amount": round(amount, 2),
            }
        else:
            # Get amount from payslip net_pay_value for regular payment
            amount = payslip.get("net_pay_value")
            if amount is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payslip '{source_payslip_id_str}' does not have a net_pay_value defined",
                    }
                )

            try:
                amount = float(amount)

                if amount < 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "net_pay_value from payslip cannot be negative",
                        }
                    )
            except (ValueError, TypeError) as e:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid net_pay_value from payslip: {str(e)}",
                    }
                )

        for payment_id, payment in payments_dict.items():
            if not isinstance(payment, dict):
                continue
            if (
                str(payment.get("employee_id")) == employee_id_str
                and str(payment.get("source_payslip_id")) == source_payslip_id_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Payment already exists for employee '{employee_id_str}' "
                            f"and payslip '{source_payslip_id_str}' (payment_id: {payment_id})"
                        ),
                    }
                )

        # Generate new payment_id
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_payment_id = generate_id(payments_dict)

        current_timestamp = "2025-11-16T23:59:00"

        # Create new payment
        new_payment = {
            "payment_id": new_payment_id,
            "employee_id": employee_id_str,
            "source_payslip_id": source_payslip_id_str,
            "payment_method": payment_method,
            "amount": round(amount, 2),
            "status": "pending",
            "payment_date": None,
            "created_at": current_timestamp,
            "last_updated": current_timestamp,
        }

        # Add to data
        payments_dict[new_payment_id] = new_payment

        result = {
            "success": True,
            "payment": new_payment,
            "message": f"Payment initiated successfully with ID: {new_payment_id}",
        }

        if calculation_details:
            result["calculation_details"] = calculation_details

        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "initiate_employee_payment",
                "description": (
                    "Initiate a payment for an employee linked to a payslip. "
                    "For final settlements (is_final_settlement=True), automatically calculates amount using: "
                    "Gross Pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5), "
                    "Total Earning = Gross Pay + payroll_earnings, "
                    "Asset Charges = (N_missing * 500) + (N_damaged * 250), "
                    "Amount = Total Earning - deductions - Asset Charges. "
                    "For regular payments (is_final_settlement=False), uses net_pay_value from the payslip. "
                    "Validates that employee exists, payslip exists and has 'draft' status. "
                    "Valid payment methods: 'Bank Transfer', 'Check'. "
                    "Sets initial status as 'pending'. "
                    "Returns the created payment details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee to initiate payment for.",
                        },
                        "source_payslip_id": {
                            "type": "string",
                            "description": "The ID of the payslip this payment is for.",
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "The payment method. Accepted values: 'Bank Transfer', 'Check'.",
                            "enum": ["Bank Transfer", "Check"],
                        },
                        "is_final_settlement": {
                            "type": "boolean",
                            "description": "Whether this is a final settlement payment. If True, amount is calculated automatically including asset charges. If False, amount is taken from payslip net_pay_value. Defaults to False.",
                        },
                    },
                    "required": [
                        "employee_id",
                        "source_payslip_id",
                        "payment_method",
                    ],
                },
            },
        }
