import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetEmployeePaymentInfo(Tool):
    """
    Retrieve payment information for an employee.
    - Returns all payments for a specific employee.
    - Can filter by source_payslip_id to get payment for a specific payslip.
    - Can filter by status (pending, completed, failed).
    - Returns payment details including amount, method, and status.
    - Returns an error if the employee doesn't exist.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        source_payslip_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payments": [...]} on success
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

        employees_dict = data.get("employees", {})
        if not isinstance(employees_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
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

        # Validate employee_id is provided
        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})

        # Convert employee_id to string for consistent comparison
        employee_id_str = str(employee_id)

        # Check if employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        # Convert source_payslip_id to string if provided
        source_payslip_id_str = str(source_payslip_id) if source_payslip_id is not None else None

        # Validate status if provided
        valid_statuses = ["pending", "completed", "failed"]
        if status is not None and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Retrieve payments for the employee
        employee_payments = []

        for payment_id, payment in payments_dict.items():
            if not isinstance(payment, dict):
                continue

            payment_employee_id = str(payment.get("employee_id", ""))
            
            # Check if this payment belongs to the employee
            if payment_employee_id != employee_id_str:
                continue

            # Filter by source_payslip_id if provided
            if source_payslip_id_str is not None:
                payment_payslip_id = str(payment.get("source_payslip_id", ""))
                if payment_payslip_id != source_payslip_id_str:
                    continue

            # Filter by status if provided
            if status is not None:
                payment_status = payment.get("status")
                if payment_status != status:
                    continue

            # Add matching payment
            payment_copy = payment.copy()
            employee_payments.append(payment_copy)

        # Sort by created_at (most recent first) for better UX
        employee_payments.sort(
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )

        return json.dumps(
            {
                "success": True,
                "payments": employee_payments,
                "count": len(employee_payments),
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
                "name": "get_employee_payment_info",
                "description": (
                    "Retrieve payment information for an employee. "
                    "Returns all payments for the specified employee. "
                    "Can optionally filter by source_payslip_id to get payment for a specific payslip. "
                    "Can optionally filter by status (pending, completed, failed). "
                    "Returns payment details including payment_id, employee_id, source_payslip_id, "
                    "payment_method, amount, status, payment_date, created_at, and last_updated. "
                    "Returns an error if the employee doesn't exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The employee ID to retrieve payments for.",
                        },
                        "source_payslip_id": {
                            "type": "string",
                            "description": "Optional. Filter payments by specific payslip ID.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. Filter payments by status. Accepted values: 'pending', 'completed', 'failed'."
                        }
                    },
                    "required": ["employee_id"],
                },
            },
        }