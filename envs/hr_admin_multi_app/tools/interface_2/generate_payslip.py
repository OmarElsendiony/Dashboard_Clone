import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GeneratePayslip(Tool):
    """
    Generate a payslip for an employee for a specific payroll cycle.
    Creates a new payslip record with calculated net pay value.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        status: Optional[str] = "draft",
    ) -> str:
        """
        Generate a payslip for an employee in a specific cycle with comprehensive calculation.
        Calculates net_pay_value considering deductions, earnings, payroll inputs, and asset charges.
        
        Business Logic:
        - Gross Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5)
        - Total Earning = Gross Pay + payroll_earning
        - Asset Charges = (N_missing × 500) + (N_damaged × 250)
        - Amount = Total Earning - deductions - Asset Charges
        
        Args:
            data: Dictionary containing payslips, employees, payroll_cycles, payroll_inputs,
                  payroll_earnings, deductions, and employee_assets
            employee_id: ID of the employee (required)
            cycle_id: ID of the payroll cycle (required)
            status: Optional status for the payslip (defaults to 'draft' if not provided)
            
        Returns:
            JSON string with success status and payslip details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        payslips = data.get("payslips", {})
        if not isinstance(payslips, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payslips container: expected dict at data['payslips']",
                }
            )
        
        employees = data.get("employees", {})
        if not isinstance(employees, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )
        
        payroll_cycles = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
                }
            )
        
        payroll_inputs = data.get("payroll_inputs", {})
        if not isinstance(payroll_inputs, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_inputs container: expected dict at data['payroll_inputs']",
                }
            )
        
        payroll_earnings = data.get("payroll_earnings", {})
        if not isinstance(payroll_earnings, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_earnings container: expected dict at data['payroll_earnings']",
                }
            )
        
        deductions = data.get("deductions", {})
        if not isinstance(deductions, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid deductions container: expected dict at data['deductions']",
                }
            )
        
        employee_assets = data.get("employee_assets", {})
        if not isinstance(employee_assets, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employee_assets container: expected dict at data['employee_assets']",
                }
            )
        
        # Validate required fields
        if not employee_id:
            return json.dumps(
                {"success": False, "error": "employee_id is required"}
            )
        
        if not cycle_id:
            return json.dumps(
                {"success": False, "error": "cycle_id is required"}
            )
        
        employee_id_str = str(employee_id)
        cycle_id_str = str(cycle_id)
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["draft", "released", "updated"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )
        
        # Validate employee exists
        if employee_id_str not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )
        
        employee = employees[employee_id_str]
        
        # Validate cycle exists
        if cycle_id_str not in payroll_cycles:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                }
            )
        
        cycle = payroll_cycles[cycle_id_str]
        
        # Check for duplicate payslip (employee_id, cycle_id must be unique)
        for existing_payslip in payslips.values():
            if (
                existing_payslip.get("employee_id") == employee_id_str
                and existing_payslip.get("cycle_id") == cycle_id_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payslip already exists for employee '{employee_id_str}' in cycle '{cycle_id_str}' (payslip_id: '{existing_payslip.get('payslip_id')}')",
                    }
                )
        
        # Find payroll input for this employee and cycle
        payroll_input = None
        for pinput in payroll_inputs.values():
            if (
                pinput.get("employee_id") == employee_id_str
                and pinput.get("cycle_id") == cycle_id_str
            ):
                payroll_input = pinput
                break
        
        # Calculate net_pay_value using the business logic formula:
        # Gross Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5)
        # Total Earning = Gross Pay + payroll_earning
        # Asset Charges = (N_missing × 500) + (N_damaged × 250)
        # Amount = Total Earning - deductions - Asset Charges
        
        base_salary = float(employee.get("base_salary", 0))
        hourly_rate = base_salary / 2080  # 52 weeks × 40 hours = 2080 annual hours
        
        if payroll_input:
            # Get hours from payroll input
            hours_worked = float(payroll_input.get("hours_worked", 0))
            overtime_hours = float(payroll_input.get("overtime_hours", 0))
        else:
            # If no payroll input exists, use default bi-weekly hours
            hours_worked = 80  # Default bi-weekly hours
            overtime_hours = 0
        
        # Calculate Gross Pay
        gross_pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5)
        
        # Calculate Total Earnings: sum of approved payroll earnings for this employee
        total_payroll_earnings = 0.0
        for earning in payroll_earnings.values():
            if (
                earning.get("employee_id") == employee_id_str
                and earning.get("status") == "approved"
            ):
                total_payroll_earnings += float(earning.get("amount", 0))
        
        total_earnings = gross_pay + total_payroll_earnings
        
        # Calculate Total Deductions: sum of valid deductions for this employee and cycle
        total_deductions = 0.0
        for deduction in deductions.values():
            if deduction.get("employee_id") == employee_id_str and deduction.get("status") == "valid":
                # Check if deduction is for this specific cycle or general (cycle_id is null)
                deduction_cycle = deduction.get("cycle_id")
                if deduction_cycle is None or deduction_cycle == cycle_id_str:
                    total_deductions += float(deduction.get("amount", 0))
        
        # Calculate Asset Charges: count missing and damaged assets
        count_missing = 0
        count_damaged = 0
        for asset in employee_assets.values():
            if asset.get("employee_id") == employee_id_str:
                asset_status = asset.get("status")
                if asset_status == "missing":
                    count_missing += 1
                elif asset_status == "damaged":
                    count_damaged += 1
        
        asset_charges = (count_missing * 500) + (count_damaged * 250)
        
        # Calculate final net pay value (Amount)
        net_pay_value = total_earnings - total_deductions - asset_charges
        net_pay_value_str = f"{net_pay_value:.2f}"
        
        timestamp = "2025-12-12T12:00:00"
        
        # Generate new payslip ID
        def generate_payslip_id(payslips_dict: Dict[str, Any]) -> str:
            if not payslips_dict:
                return "1"
            try:
                max_id = max(int(k) for k in payslips_dict.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                return "1"
        
        new_payslip_id = generate_payslip_id(payslips)
        
        # Create new payslip
        payslip_status = status if status is not None else "draft"
        
        new_payslip = {
            "payslip_id": new_payslip_id,
            "employee_id": employee_id_str,
            "cycle_id": cycle_id_str,
            "net_pay_value": net_pay_value_str,
            "status": payslip_status,
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        
        payslips[new_payslip_id] = new_payslip
        
        return json.dumps(
            {
                "success": True,
                "message": f"Payslip has been generated successfully for employee '{employee.get('full_name')}' ({employee_id_str}) in cycle '{cycle_id_str}'",
                "payslip": new_payslip,
                "action": "created",
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
                "name": "generate_payslip",
                "description": (
                    "Generate a payslip for an employee for a specific payroll cycle with comprehensive calculation. "
                    "Business Logic: Gross Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5). "
                    "Total Earning = Gross Pay + approved payroll_earnings. "
                    "Asset Charges = (N_missing × 500) + (N_damaged × 250). "
                    "Net Pay Value (Amount) = Total Earning - valid deductions - Asset Charges. "
                    "Requires employee_id and cycle_id. "
                    "Optionally accepts status ('draft', 'released', 'updated'), defaults to 'draft'. "
                    "Validates employee and cycle exist. "
                    "Prevents duplicate payslips (employee_id + cycle_id must be unique). "
                    "Considers payroll inputs (hours), payroll earnings (approved), deductions (valid), "
                    "and employee assets (missing/damaged) for exact net_pay_value calculation. "
                    "This is typically used after verifying the cycle status is 'approved'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (required)",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "ID of the payroll cycle (required)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status for the payslip ('draft', 'released', or 'updated'). Defaults to 'draft' if not provided.",
                        },
                    },
                    "required": ["employee_id", "cycle_id"],
                },
            },
        }

