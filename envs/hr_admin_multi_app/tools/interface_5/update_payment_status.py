import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class UpdatePaymentStatus(Tool):
    """
    Update the status of a payment.
    - Updates payment status (pending, completed, failed).
    - Sets payment_date when status is changed to 'completed'.
    - Validates payment exists before updating.
    - Updates the last_updated timestamp.
    - Returns the updated payment details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payment_id: str,
        status: str,
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

        payments_dict = data.get("payments", {})
        if not isinstance(payments_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payments container: expected dict at data['payments']",
                }
            )

        # Validate payment_id is provided
        if not payment_id:
            return json.dumps({"success": False, "error": "payment_id is required"})

        # Validate status is provided
        if not status:
            return json.dumps({"success": False, "error": "status is required"})

        # Convert payment_id to string for consistent comparison
        payment_id_str = str(payment_id)

        # Check if payment exists
        if payment_id_str not in payments_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payment with ID '{payment_id_str}' not found",
                }
            )

        # Get the existing payment
        payment = payments_dict[payment_id_str]
        if not isinstance(payment, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid payment data for ID '{payment_id_str}'",
                }
            )

        # Validate status
        valid_statuses = ["pending", "completed", "failed"]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Update the payment status
        payment["status"] = status

        # Set payment_date if status is 'completed'
        if status == "completed":
            payment["payment_date"] = "2025-12-12T12:00:00"

        # Update timestamp
        payment["last_updated"] = "2025-12-12T12:00:00"

        return json.dumps(
            {
                "success": True,
                "payment": payment,
                "message": f"Payment '{payment_id_str}' status updated to '{status}'",
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
                "name": "update_payment_status",
                "description": (
                    "Update the status of a payment. "
                    "Valid statuses: pending, completed, failed. "
                    "Automatically sets payment_date when status is changed to 'completed'. "
                    "Updates the last_updated timestamp automatically. "
                    "Returns the updated payment details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_id": {
                            "type": "string",
                            "description": "The ID of the payment to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "New status for the payment. Accepted values: 'pending', 'completed', 'failed'."
                        },
                    },
                    "required": ["payment_id", "status"],
                },
            },
        }
