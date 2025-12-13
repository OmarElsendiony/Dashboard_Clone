import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class UpdateCompensationPayment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payment_id: str,
        updates: Dict[str, Any],
    ) -> str:
        """
        Update an existing compensation payment.
        
        Args:
            data: The database dictionary containing all tables.
            payment_id: The ID of the payment to update (required).
            updates: JSON object containing fields to update (required).
                Supported fields: payment_method, amount, status, payment_date.
                payment_method allowed values: 'Bank Transfer', 'Check'.
                status allowed values: 'pending', 'completed', 'failed'.
        
        Returns:
            JSON string with the updated payment record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not payment_id:
            return json.dumps({"error": "Missing required parameter: payment_id is required"})
        if not updates or not isinstance(updates, dict):
            return json.dumps({"error": "Missing required parameter: updates must be a JSON object"})

        payment_id = str(payment_id)
        payments = data.get("payments", {})

        if payment_id not in payments:
            return json.dumps({"error": f"Payment with ID '{payment_id}' not found"})

        payment = payments[payment_id]

        # Validate payment_method if being updated
        if "payment_method" in updates:
            allowed_methods = ["Bank Transfer", "Check"]
            if updates["payment_method"] not in allowed_methods:
                return json.dumps({
                    "error": f"Invalid payment_method. Allowed values: {', '.join(allowed_methods)}"
                })

        # Validate status if being updated
        if "status" in updates:
            allowed_statuses = ["pending", "completed", "failed"]
            if updates["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
                })

        # Cannot update a completed payment
        if payment.get("status") == "completed" and "status" not in updates:
            return json.dumps({"error": f"Cannot update completed payment '{payment_id}'"})

        # Allowed fields to update
        allowed_fields = ["payment_method", "amount", "status", "payment_date"]

        for key, value in updates.items():
            if key in allowed_fields:
                payment[key] = value

        # Set payment_date when status changes to completed
        if updates.get("status") == "completed" and not payment.get("payment_date"):
            payment["payment_date"] = "2025-11-16T23:59:00"

        payment["last_updated"] = "2025-11-16T23:59:00"

        return json.dumps(payment)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_compensation_payment",
                "description": (
                    "Updates an existing compensation payment with the provided fields. "
                    "When status is changed to 'completed', payment_date is automatically set."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_id": {
                            "type": "string",
                            "description": "The ID of the payment to update (required).",
                        },
                        "updates": {
                            "type": "object",
                            "description": (
                                "JSON object containing fields to update (required). "
                                "Supported fields: payment_method, amount, status, payment_date."
                            ),
                            "properties": {
                                "payment_method": {
                                    "type": "string",
                                    "description": "The payment method. Allowed values: 'Bank Transfer', 'Check'.",
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "The payment amount.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The payment status. Allowed values: 'pending', 'completed', 'failed'.",
                                },
                                "payment_date": {
                                    "type": "string",
                                    "description": "The payment date in format (YYYY-MM-DD) or datetime format.",
                                },
                            },
                        },
                    },
                    "required": ["payment_id", "updates"],
                },
            },
        }
