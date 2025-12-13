import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ProcessPayment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        source_payslip_id: str,
        payment_method: str,
        amount: float,
        payment_id: Optional[str] = None,
        payment_date: Optional[str] = None,
        status: str = 'pending'
    ) -> str:
        """
        Create or update a payment transaction.
        If payment_id is provided, updates existing payment; otherwise creates new payment.
        """
        payments = data.get("payments", {})
        employees = data.get("employees", {})
        payslips = data.get("payslips", {})
        timestamp = "2025-12-12T12:00:00"
        
        # Validate required fields
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        if not source_payslip_id:
            return json.dumps({
                "success": False,
                "error": "source_payslip_id is required"
            })
        
        if not payment_method:
            return json.dumps({
                "success": False,
                "error": "payment_method is required"
            })
        
        if amount is None:
            return json.dumps({
                "success": False,
                "error": "amount is required"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        # Validate payslip exists
        if source_payslip_id not in payslips:
            return json.dumps({
                "success": False,
                "error": f"source_payslip_id '{source_payslip_id}' does not reference a valid payslip"
            })
        
        # Validate payment_method enum
        valid_payment_methods = ["Bank Transfer", "Check"]
        if payment_method not in valid_payment_methods:
            return json.dumps({
                "success": False,
                "error": f"Invalid payment_method. Must be one of: {', '.join(valid_payment_methods)}"
            })
        
        # Validate status enum
        valid_statuses = ["pending", "completed", "failed"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Check if this is an update or create
        if payment_id is not None:
            # Update existing payment
            if payment_id not in payments:
                return json.dumps({
                    "success": False,
                    "error": f"payment_id '{payment_id}' does not reference a valid payment"
                })
            
            payment = payments[payment_id]
            
            # Update fields
            payment["employee_id"] = employee_id
            payment["source_payslip_id"] = source_payslip_id
            payment["payment_method"] = payment_method
            payment["amount"] = str(amount)
            payment["status"] = status
            if payment_date is not None:
                payment["payment_date"] = payment_date
            payment["last_updated"] = timestamp
            
            return json.dumps({
                "success": True,
                "payment": payment
            })
        else:
            # Create new payment
            def generate_id(table: Dict[str, Any]) -> str:
                if not table:
                    return "1"
                return str(max(int(k) for k in table.keys()) + 1)
            
            new_payment_id = generate_id(payments)
            
            # Create new payment record
            new_payment = {
                "payment_id": new_payment_id,
                "employee_id": employee_id,
                "source_payslip_id": source_payslip_id,
                "payment_method": payment_method,
                "amount": str(amount),
                "status": status,
                "payment_date": payment_date if payment_date else None,
                "created_at": timestamp,
                "last_updated": timestamp
            }
            
            payments[new_payment_id] = new_payment
            
            return json.dumps({
                "success": True,
                "payment": new_payment
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "process_payment",
                "description": "Create or update a payment transaction. If payment_id is provided, updates existing payment; otherwise creates new payment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_id": {
                            "type": "string",
                            "description": "Payment ID (optional, if provided will update existing payment, otherwise creates new)"
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "source_payslip_id": {
                            "type": "string",
                            "description": "Source payslip ID (required)"
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Payment method: 'Bank Transfer' or 'Check' (required)",
                            "enum": ["Bank Transfer", "Check"]
                        },
                        "amount": {
                            "type": "number",
                            "description": "Payment amount (required)"
                        },
                        "payment_date": {
                            "type": "string",
                            "description": "Payment date (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Payment status: pending, completed, failed (optional, default: 'pending')",
                            "enum": ["pending", "completed", "failed"]
                        }
                    },
                    "required": ["employee_id", "source_payslip_id", "payment_method", "amount"]
                }
            }
        }
