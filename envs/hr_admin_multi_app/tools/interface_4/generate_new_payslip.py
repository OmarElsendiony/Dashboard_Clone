import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class GenerateNewPayslip(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        status: str = 'draft'
    ) -> str:
        """
        Generate a new payslip record by calculating net pay based on:
        - Employee base salary (to calculate hourly rate)
        - Hours worked and overtime from payroll_inputs
        - Approved payroll earnings
        - Deductions
        - Asset charges (missing/damaged assets)
        """
        payslips = data.get("payslips", {})
        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        payroll_inputs = data.get("payroll_inputs", {})
        payroll_earnings = data.get("payroll_earnings", {})
        deductions = data.get("deductions", {})
        employee_assets = data.get("employee_assets", {})
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
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        employee = employees[employee_id]
        
        # Validate cycle exists
        if cycle_id not in payroll_cycles:
            return json.dumps({
                "success": False,
                "error": f"cycle_id '{cycle_id}' does not reference a valid payroll cycle"
            })
        
        # Validate status
        valid_statuses = ["draft", "released", "updated"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Check if payslip already exists for this employee and cycle (unique constraint)
        for payslip_id, payslip in payslips.items():
            if payslip.get("employee_id") == employee_id and payslip.get("cycle_id") == cycle_id:
                return json.dumps({
                    "success": False,
                    "error": f"A payslip already exists for employee_id '{employee_id}' and cycle_id '{cycle_id}' (payslip_id: '{payslip_id}')"
                })
        
        # Get base salary and calculate hourly rate
        # Formula: Hourly Rate = Annual Base Salary / (26 weeks × 80 hours/week) = Annual Base Salary / 2080
        base_salary = float(employee.get("base_salary", 0))
        if base_salary <= 0:
            return json.dumps({
                "success": False,
                "error": f"Employee '{employee_id}' has invalid base_salary: {base_salary}"
            })
        
        hourly_rate = base_salary / 2080.0
        
        # Get hours_worked and overtime_hours from payroll_inputs for this employee and cycle
        hours_worked = 0.0
        overtime_hours = 0.0
        payroll_input_found = False
        
        for input_id, payroll_input in payroll_inputs.items():
            if (payroll_input.get("employee_id") == employee_id and 
                payroll_input.get("cycle_id") == cycle_id):
                hours_worked = float(payroll_input.get("hours_worked", 0))
                overtime_hours = float(payroll_input.get("overtime_hours", 0))
                payroll_input_found = True
                break
        
        if not payroll_input_found:
            return json.dumps({
                "success": False,
                "error": f"No payroll_input found for employee_id '{employee_id}' and cycle_id '{cycle_id}'"
            })
        
        # Calculate Gross Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5)
        gross_pay = (hours_worked * hourly_rate) + (overtime_hours * hourly_rate * 1.5)
        
        # Get approved payroll earnings for the employee
        total_earnings = 0.0
        for earning_id, earning in payroll_earnings.items():
            if (earning.get("employee_id") == employee_id and 
                earning.get("status") == "approved"):
                total_earnings += float(earning.get("amount", 0))
        
        # Calculate Total Earning = Gross Pay + payroll_earnings
        total_earning = gross_pay + total_earnings
        
        # Get deductions for the employee (matching cycle_id or null cycle_id)
        total_deductions = 0.0
        for deduction_id, deduction in deductions.items():
            if deduction.get("employee_id") != employee_id:
                continue
            deduction_cycle_id = deduction.get("cycle_id")
            if deduction_cycle_id is None or deduction_cycle_id == cycle_id:
                if deduction.get("status") == "valid":
                    total_deductions += float(deduction.get("amount", 0))
        
        # Calculate Asset Charges = (N_missing * 500) + (N_damaged * 250)
        asset_charges = 0.0
        missing_count = 0
        damaged_count = 0
        
        for asset_id, asset in employee_assets.items():
            if asset.get("employee_id") == employee_id:
                asset_status = asset.get("status")
                if asset_status == "missing":
                    missing_count += 1
                elif asset_status == "damaged":
                    damaged_count += 1
        
        asset_charges = (missing_count * 500.0) + (damaged_count * 250.0)
        
        # Calculate Net Pay = Total Earning - deductions - Asset Charges
        net_pay_value = total_earning - total_deductions - asset_charges
        
        # Generate new payslip_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_payslip_id = generate_id(payslips)
        
        # Create new payslip record
        new_payslip = {
            "payslip_id": new_payslip_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "net_pay_value": str(round(net_pay_value, 2)),
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        payslips[new_payslip_id] = new_payslip
        
        return json.dumps({
            "success": True,
            "payslip": new_payslip,
            "calculation_details": {
                "base_salary": round(base_salary, 2),
                "hourly_rate": round(hourly_rate, 2),
                "hours_worked": round(hours_worked, 2),
                "overtime_hours": round(overtime_hours, 2),
                "gross_pay": round(gross_pay, 2),
                "total_earnings": round(total_earnings, 2),
                "total_earning": round(total_earning, 2),
                "total_deductions": round(total_deductions, 2),
                "asset_charges": round(asset_charges, 2),
                "missing_assets": missing_count,
                "damaged_assets": damaged_count,
                "net_pay_value": round(net_pay_value, 2)
            }
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "generate_new_payslip",
                "description": "Generate a new payslip record by calculating net pay. Calculates hourly rate from base salary (Annual Base Salary / 2080), gets hours worked from payroll_inputs, calculates gross pay, adds approved earnings, subtracts deductions and asset charges. Formula: Net Pay = (Gross Pay + Earnings) - Deductions - Asset Charges, where Gross Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5), Asset Charges = (missing_assets × 500) + (damaged_assets × 250).",
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
                        "status": {
                            "type": "string",
                            "description": "Payslip status: draft, released, updated (optional, default: 'draft')",
                            "enum": ["draft", "released", "updated"]
                        }
                    },
                    "required": ["employee_id", "cycle_id"]
                }
            }
        }
