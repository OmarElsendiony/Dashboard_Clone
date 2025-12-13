import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdatePayrollPayment(Tool):
    """
    Update a payroll payment status and payment date.
    Used to mark payments as completed or failed.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payment_id: str,
        status: Optional[str] = None,
        payment_date: Optional[str] = None,
    ) -> str:
        """
        Update a payroll payment's status and/or payment date.
        
        Args:
            data: Dictionary containing payments
            payment_id: ID of the payment (required)
            status: Optional status to set ('pending', 'completed', 'failed')
            payment_date: Optional payment date (YYYY-MM-DD format or datetime string)
            
        Returns:
            JSON string with success status and updated payment details
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
        
        # Validate required fields
        if not payment_id:
            return json.dumps(
                {"success": False, "error": "payment_id is required"}
            )
        
        payment_id_str = str(payment_id)
        
        # Validate payment exists
        if payment_id_str not in payments:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payment with ID '{payment_id_str}' not found",
                }
            )
        
        payment = payments[payment_id_str]
        
        # Validate status if provided
        valid_statuses = ["pending", "completed", "failed"]
        if status and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                }
            )
        
        timestamp = "2025-12-12T12:00:00"
        
        previous_status = payment.get("status")
        previous_payment_date = payment.get("payment_date")
        
        # Update fields
        updated_fields = []
        
        if status:
            # Only update and log if status is actually changing
            if status != previous_status:
                payment["status"] = status
                updated_fields.append(f"status: '{previous_status}' -> '{status}'")
        
        if payment_date is not None:
            # Handle payment_date - only update if explicitly provided
            if payment_date == "":
                payment["payment_date"] = None
                if previous_payment_date is not None:
                    updated_fields.append(f"payment_date: '{previous_payment_date}' -> null")
            else:
                payment_date_str = str(payment_date)
                payment["payment_date"] = payment_date_str
                if previous_payment_date != payment_date_str:
                    updated_fields.append(f"payment_date: '{previous_payment_date}' -> '{payment_date_str}'")
        
        payment["last_updated"] = timestamp
        
        if not updated_fields:
            return json.dumps(
                {
                    "success": False,
                    "error": "No fields to update. Please provide status or payment_date.",
                }
            )
        
        return json.dumps(
            {
                "success": True,
                "message": f"Payment '{payment_id_str}' has been updated successfully. Updated: {', '.join(updated_fields)}",
                "payment": payment,
                "previous_status": previous_status,
                "action": "updated",
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
                "name": "update_payroll_payment",
                "description": (
                    "Update a payroll payment's status and/or payment date. "
                    "Validates payment exists and status is valid. "
                    "Valid statuses: 'pending', 'completed', 'failed'. "
                    "Only updates fields that are explicitly provided. "
                    "Does not automatically change payment_date based on status - payment_date must be explicitly provided to change it. "
                    "This is typically used to mark payments as completed or failed based on payment processing results."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_id": {
                            "type": "string",
                            "description": "ID of the payment to update (required)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional: Status to set. Valid values: 'pending', 'completed', 'failed'",
                            "enum": ["pending", "completed", "failed"],
                        },
                        "payment_date": {
                            "type": "string",
                            "description": "Optional: Payment date to set (YYYY-MM-DD format or datetime string). Set to empty string to clear.",
                        },
                    },
                    "required": ["payment_id"],
                },
            },
        }

