import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class CreateCompensationPayment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        source_payslip_id: str,
        amount: float,
        payment_method: str,
    ) -> str:
        """
        Create a compensation payment for an employee linked to a payslip.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee (required).
            source_payslip_id: The ID of the source payslip (required).
            amount: The payment amount (required).
            payment_method: The payment method. Allowed values: 'Bank Transfer', 'Check' (required).
        
        Returns:
            JSON string with the created payment record.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            max_id = 0
            for k in table.keys():
                try:
                    max_id = max(max_id, int(k))
                except ValueError:
                    continue
            return str(max_id + 1)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})
        if not source_payslip_id:
            return json.dumps({"error": "Missing required parameter: source_payslip_id is required"})
        if amount is None:
            return json.dumps({"error": "Missing required parameter: amount is required"})
        if not payment_method:
            return json.dumps({"error": "Missing required parameter: payment_method is required"})

        # Validate payment_method
        allowed_methods = ["Bank Transfer", "Check"]
        if payment_method not in allowed_methods:
            return json.dumps({
                "error": f"Invalid payment_method. Allowed values: {', '.join(allowed_methods)}"
            })

        employee_id = str(employee_id)
        source_payslip_id = str(source_payslip_id)

        employees = data.get("employees", {})
        payslips = data.get("payslips", {})
        payments = data.get("payments", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        # Validate source_payslip_id
        if source_payslip_id not in payslips:
            return json.dumps({"error": f"Payslip with ID '{source_payslip_id}' not found"})

        # Verify payslip belongs to the employee
        payslip = payslips[source_payslip_id]
        if payslip.get("employee_id") != employee_id:
            return json.dumps({
                "error": f"Payslip '{source_payslip_id}' does not belong to employee '{employee_id}'"
            })

        if float(amount) <= 0:
            return json.dumps({"error": "Payment amount must be greater than 0"})

        # Generate new payment ID
        payment_id = generate_id(payments)

        # Create payment record
        timestamp = "2025-11-16T23:59:00"
        new_payment = {
            "payment_id": payment_id,
            "employee_id": employee_id,
            "source_payslip_id": source_payslip_id,
            "payment_method": payment_method,
            "amount": float(amount),
            "status": "pending",
            "payment_date": None,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        payments[payment_id] = new_payment
        data["payments"] = payments

        return json.dumps(new_payment)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_compensation_payment",
                "description": (
                    "Creates a compensation payment for an employee linked to a payslip. "
                    "Payment is created with 'pending' status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee (required).",
                        },
                        "source_payslip_id": {
                            "type": "string",
                            "description": "The ID of the source payslip (required).",
                        },
                        "amount": {
                            "type": "number",
                            "description": "The payment amount (required).",
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "The payment method. Allowed values: 'Bank Transfer', 'Check' (required).",
                        },
                    },
                    "required": ["employee_id", "source_payslip_id", "amount", "payment_method"],
                },
            },
        }
