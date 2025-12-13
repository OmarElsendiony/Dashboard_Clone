import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreatePayslip(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], employee_id: str, cycle_id: str) -> str:
        """
        Create payslip records for employees with automatic net pay calculation.
        
        Args:
            data: Environment data containing employees, payroll_cycles, payslips, 
                  payroll_inputs, payroll_earnings, and deductions
            employee_id: The employee identifier (required)
            cycle_id: The payroll cycle identifier (required)
        
        Net pay is automatically calculated as:
        Gross Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5) + allowance_amount
        Where: hourly_rate = base_salary / (52 × 80)
        Net Pay = Gross Pay + Approved Earnings - Valid Deductions
        """
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        timestamp = "2025-11-22T12:00:00"
        payslips = data.get("payslips", {})
        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        payroll_inputs = data.get("payroll_inputs", {})
        payroll_earnings = data.get("payroll_earnings", {})
        deductions = data.get("deductions", {})
        
        # Validate required parameters
        if not all([employee_id, cycle_id]):
            return json.dumps({
                "success": False,
                "error": "Missing required parameters. Required: employee_id, cycle_id"
            })
        
        # Validate that employee exists and has active status
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"Halt: Employee not found or inactive"
            })
        
        employee = employees[employee_id]
        if employee.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"Halt: Employee not found or inactive"
            })
        
        # Validate that payroll cycle exists
        if cycle_id not in payroll_cycles:
            return json.dumps({
                "success": False,
                "error": f"Halt: Payroll cycle not found"
            })
        
        # Validate that payroll cycle is in open or approved status
        cycle = payroll_cycles[cycle_id]
        if cycle.get("status") not in ["open", "approved"]:
            return json.dumps({
                "success": False,
                "error": f"Halt: Payroll cycle must be in 'open' or 'approved' status"
            })
        
        # Check for duplicate payslip (employee_id, cycle_id must be unique)
        for existing_payslip in payslips.values():
            if (existing_payslip.get("employee_id") == employee_id and 
                existing_payslip.get("cycle_id") == cycle_id):
                return json.dumps({
                    "success": False,
                    "error": f"Halt: Payslip already exists for employee {employee_id} in cycle {cycle_id}"
                })
        
        # Find payroll input for this employee and cycle
        payroll_input = None
        for pi in payroll_inputs.values():
            if pi.get("employee_id") == employee_id and pi.get("cycle_id") == cycle_id:
                payroll_input = pi
                break
        
        if not payroll_input:
            return json.dumps({
                "success": False,
                "error": f"Halt: No payroll input found for employee {employee_id} in cycle {cycle_id}"
            })
        
        # Get employee base salary
        base_salary = employee.get("base_salary")
        if base_salary is None or base_salary <= 0:
            return json.dumps({
                "success": False,
                "error": f"Halt: Invalid or missing base salary for employee"
            })
        
        # Calculate hourly rate
        # Formula: Hourly Rate = Annual Base Salary / (52 weeks × 80 hours/week)
        hourly_rate = float(base_salary) / (52 * 80)
        
        # Get payroll input values
        hours_worked = float(payroll_input.get("hours_worked", 0))
        overtime_hours = float(payroll_input.get("overtime_hours", 0))
        allowance_amount = float(payroll_input.get("allowance_amount", 0))
        
        # Calculate gross pay from inputs
        # Total Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5) + allowance_amount
        regular_pay = hours_worked * hourly_rate
        overtime_pay = overtime_hours * hourly_rate * 1.5
        gross_pay = regular_pay + overtime_pay + allowance_amount
        
        # Add approved earnings for this employee and cycle
        additional_earnings = 0
        for earning in payroll_earnings.values():
            if (earning.get("employee_id") == employee_id and 
                earning.get("cycle_id") == cycle_id and
                earning.get("status") == "approved"):
                additional_earnings += float(earning.get("amount", 0))
        
        # Subtract valid deductions for this employee
        # Note: Deductions are not cycle-specific in the schema, so we include all valid deductions
        total_deductions = 0
        for deduction in deductions.values():
            if (deduction.get("employee_id") == employee_id and
                deduction.get("status") == "valid"):
                total_deductions += float(deduction.get("amount", 0))
        
        # Calculate net pay
        net_pay_value = gross_pay + additional_earnings - total_deductions
        
        # Ensure net pay is not negative
        if net_pay_value < 0:
            return json.dumps({
                "success": False,
                "error": f"Halt: Calculated net pay is negative ({net_pay_value:.2f}). Check deductions and earnings."
            })
        
        # Round to 2 decimal places for currency
        net_pay_value = round(net_pay_value, 2)
        
        # Generate new payslip ID
        new_payslip_id = generate_id(payslips)
        
        # Create new payslip record
        new_payslip = {
            "payslip_id": new_payslip_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "net_pay_value": net_pay_value,
            "status": "draft",
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        payslips[new_payslip_id] = new_payslip
        
        return json.dumps(new_payslip)
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_payslip",
                "description": "Create payslip records for employees in the payroll system with automatic net pay calculation. This tool establishes new payslips by calculating net pay from payroll inputs, approved earnings, and valid deductions. Formula: Gross Pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5) + allowance_amount, where hourly_rate = base_salary / (52 × 80). Net Pay = Gross Pay + Approved Earnings - Valid Deductions. Validates that employees have active status, payroll cycles are in 'open' or 'approved' status, payroll inputs exist for the cycle, and prevents duplicate payslips for the same employee and cycle combination. Ensures calculated net pay is non-negative. Essential for payroll processing, employee compensation management, and maintaining accurate payslip records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee identifier (required, must exist with active status)"
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Payroll cycle identifier (required, must exist with 'open' or 'approved' status, must have payroll input for employee)"
                        }
                    },
                    "required": ["employee_id", "cycle_id"]
                }
            }
        }