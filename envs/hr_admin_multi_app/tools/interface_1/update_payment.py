import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdatePayment(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], payment_id: str, status: Optional[str] = None, 
               payment_date: Optional[str] = None, amount: Optional[float] = None) -> str:
        """
        Update payment records in the payroll system.
        
        Args:
            data: Environment data containing payments
            payment_id: The payment identifier (required)
            status: The payment status - 'pending', 'completed', 'failed' (optional)
            payment_date: The payment date in YYYY-MM-DD format (optional)
            amount: Updated payment amount (optional)
        """
        timestamp = "2025-11-22T12:00:00"
        payments = data.get("payments", {})
        
        # Validate required parameter
        if not payment_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: payment_id"
            })
        
        # Validate that payment exists
        if payment_id not in payments:
            return json.dumps({
                "success": False,
                "error": f"Halt: Payment not found"
            })
        
        # Validate at least one optional field is provided
        if status is None and payment_date is None and amount is None:
            return json.dumps({
                "success": False,
                "error": "At least one optional parameter (status, payment_date, amount) must be provided for updates"
            })
        
        # Get current payment
        current_payment = payments[payment_id]
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["pending", "completed", "failed"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Halt: Payment operation failed - status must be one of: {', '.join(valid_statuses)}"
                })
        
        # Validate amount if provided
        if amount is not None:
            try:
                amount = float(amount)
                if amount <= 0:
                    return json.dumps({
                        "success": False,
                        "error": "Halt: Payment operation failed - amount must be positive"
                    })
            except (ValueError, TypeError):
                return json.dumps({
                    "success": False,
                    "error": "Halt: Payment operation failed - invalid amount format"
                })
        
        # Validate payment_date format if provided
        if payment_date is not None:
            try:
                # Basic date format validation for YYYY-MM-DD
                parts = payment_date.split('-')
                if len(parts) != 3:
                    raise ValueError("Invalid date format")
                year, month, day = map(int, parts)
                if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                    raise ValueError("Invalid date values")
            except (ValueError, AttributeError):
                return json.dumps({
                    "success": False,
                    "error": "Halt: Payment operation failed - invalid payment_date format. Use YYYY-MM-DD"
                })
        
        # Update payment record
        updated_payment = current_payment.copy()
        
        if status is not None:
            updated_payment["status"] = status
        
        if payment_date is not None:
            updated_payment["payment_date"] = payment_date
        
        if amount is not None:
            updated_payment["amount"] = amount
        
        updated_payment["last_updated"] = timestamp
        payments[payment_id] = updated_payment
        
        return json.dumps(updated_payment)
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_payment",
                "description": "Update payment records in the payroll system. This tool modifies existing payment transactions while maintaining data integrity. Allows updates to payment status, payment date, and payment amounts. Validates status values against accepted options ('pending', 'completed', 'failed'), ensures payment dates follow YYYY-MM-DD format, and confirms amounts remain positive. Essential for payment processing, transaction tracking, and maintaining accurate payment records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_id": {
                            "type": "string",
                            "description": "Payment identifier (required, must exist in system)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Payment status: 'pending', 'completed', 'failed' (optional)",
                        },
                        "payment_date": {
                            "type": "string",
                            "description": "Payment date in YYYY-MM-DD format (optional)"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Updated payment amount (optional, must be positive monetary value)"
                        }
                    },
                    "required": ["payment_id"]
                }
            }
        }
