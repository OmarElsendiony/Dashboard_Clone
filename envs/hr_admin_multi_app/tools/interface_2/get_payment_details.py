import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetPaymentDetails(Tool):
    """
    Retrieve payment details by payment ID.
    Used to get information about a specific payment record.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payment_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        source_payslip_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Retrieve payment details with flexible filtering options.
        
        All parameters are optional. If payment_id is provided, returns that specific payment.
        Otherwise, filters payments based on provided criteria (employee_id, source_payslip_id, 
        payment_method, status). If no parameters are provided, returns all payments.
        
        Args:
            data: Dictionary containing payments
            payment_id: ID of the payment (optional)
            employee_id: Filter by employee ID (optional)
            source_payslip_id: Filter by source payslip ID (optional)
            payment_method: Filter by payment method - "Bank Transfer" or "Check" (optional)
            status: Filter by payment status - "pending", "completed", or "failed" (optional)
            
        Returns:
            JSON string with success status and payment details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        payments = data.get("payments", {})
        if not isinstance(payments, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payments container: expected dict at data['payments']",
                }
            )
        
        # Validate payment_method if provided
        if payment_method is not None:
            valid_payment_methods = ["Bank Transfer", "Check"]
            if payment_method not in valid_payment_methods:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid payment_method: '{payment_method}'. Must be one of {valid_payment_methods}",
                    }
                )
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["pending", "completed", "failed"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status: '{status}'. Must be one of {valid_statuses}",
                    }
                )
        
        # If payment_id is provided, retrieve that specific payment
        if payment_id is not None:
            payment_id_str = str(payment_id)
            
            if payment_id_str not in payments:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payment with ID '{payment_id_str}' not found",
                    }
                )
            
            payment = payments[payment_id_str]
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Retrieved payment '{payment_id_str}' for employee '{payment.get('employee_id')}' with status '{payment.get('status')}'",
                    "payment": payment,
                }
            )
        
        # Otherwise, filter payments based on provided criteria
        filtered_payments = []
        
        for payment in payments.values():
            # Apply employee_id filter
            if employee_id is not None:
                if payment.get("employee_id") != str(employee_id):
                    continue
            
            # Apply source_payslip_id filter
            if source_payslip_id is not None:
                if payment.get("source_payslip_id") != str(source_payslip_id):
                    continue
            
            # Apply payment_method filter
            if payment_method is not None:
                if payment.get("payment_method") != payment_method:
                    continue
            
            # Apply status filter
            if status is not None:
                if payment.get("status") != status:
                    continue
            
            filtered_payments.append(payment)
        
        if not filtered_payments:
            return json.dumps(
                {
                    "success": False,
                    "error": "No payments found matching the specified criteria",
                }
            )
        
        return json.dumps(
            {
                "success": True,
                "message": f"Retrieved {len(filtered_payments)} payment(s) matching the criteria",
                "payments": filtered_payments,
                "count": len(filtered_payments),
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
                "name": "get_payment_details",
                "description": (
                    "Retrieve payment details with flexible filtering options. "
                    "All parameters are optional. If payment_id is provided, returns that specific payment. "
                    "Otherwise, filters payments based on any combination of: employee_id, source_payslip_id, payment_method, status. "
                    "If no parameters are provided, returns all payments. "
                    "Returns complete payment information including payment_id, employee_id, source_payslip_id, "
                    "payment_method, amount, status, payment_date, created_at, and last_updated. "
                    "Valid payment statuses: 'pending', 'completed', 'failed'. "
                    "Valid payment methods: 'Bank Transfer', 'Check'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_id": {
                            "type": "string",
                            "description": "ID of the payment (optional). If provided, returns that specific payment.",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Filter by employee ID (optional). Returns all payments for the specified employee.",
                        },
                        "source_payslip_id": {
                            "type": "string",
                            "description": "Filter by source payslip ID (optional). Returns the payment associated with the specified payslip.",
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Filter by payment method (optional). Valid values: 'Bank Transfer', 'Check'.",
                            "enum": ["Bank Transfer", "Check"],
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by payment status (optional). Valid values: 'pending', 'completed', 'failed'.",
                            "enum": ["pending", "completed", "failed"],
                        },
                    },
                    "required": [],
                },
            },
        }

