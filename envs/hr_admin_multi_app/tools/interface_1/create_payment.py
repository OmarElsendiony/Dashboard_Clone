import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreatePayment(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], employee_id: str, payment_method: str, amount: float, 
               cycle_id: Optional[str] = None, source_payslip_id: Optional[str] = None) -> str:
        """
        Create payment records for employees.
        
        Args:
            data: Environment data containing employees, payments, payroll_cycles, and payslips
            employee_id: The employee identifier (required)
            payment_method: The payment method (required)
            amount: The payment amount (required)
            cycle_id: The payroll cycle identifier (optional)
            source_payslip_id: The source payslip identifier (optional)
        """
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        timestamp = "2025-11-22T12:00:00"
        payments = data.get("payments", {})
        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        payslips = data.get("payslips", {})
        
        # Validate required parameters
        if not all([employee_id, payment_method, amount is not None]):
            return json.dumps({
                "success": False,
                "error": "Missing required parameters. Required: employee_id, payment_method, amount"
            })
        
# Validate payment_method is one of the allowed values
        valid_payment_methods = ["Bank Transfer", "Check"]
        if payment_method.strip() not in valid_payment_methods:
            return json.dumps({
                "success": False,
                "error": f"Halt: Invalid payment method - must be one of: {', '.join(valid_payment_methods)}"
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
        
        # Validate cycle_id if provided
        if cycle_id is not None:
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
        
        # Validate source_payslip_id if provided
        if source_payslip_id is not None:
            if source_payslip_id not in payslips:
                return json.dumps({
                    "success": False,
                    "error": f"Halt: Source payslip not found"
                })
            
            # Validate that payslip belongs to the same employee
            source_payslip = payslips[source_payslip_id]
            if source_payslip.get("employee_id") != employee_id:
                return json.dumps({
                    "success": False,
                    "error": f"Halt: Source payslip does not belong to the specified employee"
                })
            
            # Validate that payslip status is released (can't pay draft payslips)
            if source_payslip.get("status") not in ["released", "updated"]:
                return json.dumps({
                    "success": False,
                    "error": f"Halt: Source payslip must be in 'released' or 'updated' status"
                })
            
            # If cycle_id is provided, validate consistency between cycle and payslip
            if cycle_id is not None:
                if source_payslip.get("cycle_id") != cycle_id:
                    return json.dumps({
                        "success": False,
                        "error": f"Halt: Source payslip cycle does not match the specified cycle"
                    })
        
        # Validate amount is positive monetary value
        try:
            amount = float(amount)
            if amount <= 0:
                return json.dumps({
                    "success": False,
                    "error": "Halt: Invalid payment amount - amount must be positive"
                })
        except (ValueError, TypeError):
            return json.dumps({
                "success": False,
                "error": "Halt: Invalid payment amount - invalid amount format"
            })
        
        # Validate payment_method is not empty
        if not payment_method or not payment_method.strip():
            return json.dumps({
                "success": False,
                "error": "Halt: Invalid payment method - payment_method cannot be empty"
            })
        
        # Generate new payment ID
        new_payment_id = generate_id(payments)
        
        # Create new payment record
        new_payment = {
            "payment_id": new_payment_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "source_payslip_id": source_payslip_id,
            "payment_method": payment_method.strip(),
            "amount": amount,
            "status": "pending",
            "payment_date": None,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        payments[new_payment_id] = new_payment
        
        return json.dumps(new_payment)
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_payment",
                "description": "Create payment records for employees in the payroll system. This tool establishes new payment transactions with proper validation of employee existence and active status, payment amounts, payroll cycle status verification, and source payslip validation. Validates that employees exist with active status, payment amounts are positive monetary values, payment methods are specified, payroll cycles are in 'open' or 'approved' status, and source payslips belong to the correct employee with 'released' or 'updated' status. Ensures consistency between cycle_id and source payslip's cycle. Essential for payment processing, employee compensation disbursement, and maintaining accurate payment records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee identifier (required, must exist in system)"
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Payment method: 'Bank Transfer' or 'Check' (required)"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Payment amount (required, must be positive monetary value)"
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Payroll cycle identifier (optional, links payment to payroll cycle)"
                        },
                        "source_payslip_id": {
                            "type": "string",
                            "description": "Source payslip identifier (optional, links payment to specific payslip)"
                        }
                    },
                    "required": ["employee_id", "payment_method", "amount"]
                }
            }
        }
