import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CalculatePayroll(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str
    ) -> str:
        """
        Calculate final settlement payroll for an employee.
        Calculates based on approved earnings, deductions, and any outstanding amounts.
        """
        employees = data.get("employees", {})
        payroll_earnings = data.get("payroll_earnings", {})
        deductions = data.get("deductions", {})
        payslips = data.get("payslips", {})
        finance_settlements = data.get("finance_settlements", {})
        exit_cases = data.get("exit_cases", {})
        
        # Validate required field
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        employee = employees[employee_id]
        
        # Check if exit case exists and is cleared (SOP 19 requirement)
        exit_case = None
        for case_id, case in exit_cases.items():
            if case.get("employee_id") == employee_id:
                exit_case = case
                break
        
        if exit_case:
            if exit_case.get("exit_clearance_status") != "cleared":
                return json.dumps({
                    "success": False,
                    "error": f"Exit clearance is not completed for employee_id '{employee_id}'. Exit clearance status must be 'cleared' before calculating settlement."
                })
        
        # Calculate total approved earnings (not yet paid)
        total_approved_earnings = 0.0
        for earning_id, earning in payroll_earnings.items():
            if (earning.get("employee_id") == employee_id and 
                earning.get("status") == "approved"):
                total_approved_earnings += float(earning.get("amount", 0))
        
        # Calculate total outstanding deductions
        total_deductions = 0.0
        for deduction_id, deduction in deductions.items():
            if (deduction.get("employee_id") == employee_id and 
                deduction.get("status") == "valid"):
                total_deductions += float(deduction.get("amount", 0))
        
        # Get latest released payslip net pay value (if any)
        latest_payslip_net_pay = 0.0
        latest_payslip_id = None
        for payslip_id, payslip in payslips.items():
            if (payslip.get("employee_id") == employee_id and 
                payslip.get("status") == "released"):
                net_pay = float(payslip.get("net_pay_value", 0))
                if net_pay > latest_payslip_net_pay:
                    latest_payslip_net_pay = net_pay
                    latest_payslip_id = payslip_id
        
        # Check for existing finance settlements
        existing_settlement_amount = 0.0
        for settlement_id, settlement in finance_settlements.items():
            if (settlement.get("employee_id") == employee_id and 
                not settlement.get("is_cleared", False)):
                existing_settlement_amount += float(settlement.get("amount", 0))
        
        # Calculate final settlement amount
        # Settlement = Approved Earnings - Deductions + Base Salary (if applicable)
        # For exit settlement, we consider approved earnings minus deductions
        # Base salary would typically be included in the latest payslip
        base_salary = float(employee.get("base_salary", 0))
        
        # Final settlement calculation:
        # Sum of approved earnings + base salary (if not already in payslip) - deductions
        # For simplicity, we'll calculate: approved earnings - deductions
        # The base salary is typically already accounted for in payslips
        settlement_amount = total_approved_earnings - total_deductions
        
        # If there's a latest payslip, we might want to include its net pay
        # But for settlement, we typically calculate what's outstanding
        # So we focus on unpaid approved earnings minus outstanding deductions
        
        return json.dumps({
            "success": True,
            "employee_id": employee_id,
            "settlement_amount": round(settlement_amount, 2),
            "total_approved_earnings": round(total_approved_earnings, 2),
            "total_deductions": round(total_deductions, 2),
            "latest_payslip_net_pay": round(latest_payslip_net_pay, 2),
            "latest_payslip_id": latest_payslip_id,
            "existing_settlement_amount": round(existing_settlement_amount, 2),
            "base_salary": round(base_salary, 2)
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "calculate_payroll",
                "description": "Calculate final settlement payroll for an employee. Calculates based on approved earnings, deductions, and outstanding amounts. Requires exit clearance to be completed if exit case exists.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        }
                    },
                    "required": ["employee_id"]
                }
            }
        }
