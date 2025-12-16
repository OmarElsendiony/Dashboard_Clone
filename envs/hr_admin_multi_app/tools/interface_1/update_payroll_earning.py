import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdatePayrollEarning(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        earning_id: str,
        amount: Optional[float] = None,
        status: Optional[str] = None,
        earning_type: Optional[str] = None,
    ) -> str:
        """
        Updates an existing payroll earning record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not earning_id:
            return json.dumps({"error": "earning_id is required"})

        # Convert IDs to strings for consistent comparison
        earning_id = str(earning_id)

        payroll_earnings = data.get("payroll_earnings", {})
        if earning_id not in payroll_earnings:
            return json.dumps(
                {"error": f"Payroll earning with ID '{earning_id}' not found"}
            )

        if amount is None and status is None and earning_type is None:
            return json.dumps(
                {"error": "No fields provided to update. Provide at least one field"}
            )

        current_earning = payroll_earnings[earning_id]

        if amount is not None and amount <= 0:
            return json.dumps(
                {"error": "amount must be a positive number when provided"}
            )

        allowed_statuses = ["pending", "approved", "rejected", "require_justification"]
        allowed_earning_types = ["bonus", "incentive", "allowance", "overtime"]

        new_earning_type = (
            earning_type
            if earning_type is not None
            else current_earning.get("earning_type")
        )
        new_amount = amount if amount is not None else current_earning.get("amount")
        new_status = status if status is not None else current_earning.get("status")

        if new_earning_type not in allowed_earning_types:
            return json.dumps(
                {
                    "error": "Invalid earning_type. Allowed values: 'bonus', 'incentive', 'allowance', 'overtime'"
                }
            )

        if new_status not in allowed_statuses:
            return json.dumps(
                {
                    "error": "Invalid status. Allowed values: "
                    "'pending', 'approved', 'rejected', 'require_justification'"
                }
            )

        # Enforce justification rule for high-value bonuses
        if new_earning_type == "bonus" and new_amount is not None and new_amount > 5000:
            # For bonuses over $5000, status must be 'require_justification'
            if new_status not in ["require_justification", "approved", "rejected"]:
                new_status = "require_justification"

        # SOP 11, Step 4: Check for conflicting/duplicate earnings before approving or rejecting
        if status is not None and status in ["approved", "rejected"]:
            employee_id = current_earning.get("employee_id")
            cycle_id = current_earning.get("cycle_id")

            for other_id, other_earning in payroll_earnings.items():
                if other_id == earning_id:
                    continue
                if (
                    other_earning.get("employee_id") == employee_id
                    and other_earning.get("cycle_id") == cycle_id
                    and other_earning.get("earning_type") == new_earning_type
                    and other_earning.get("status") == "approved"
                ):
                    return json.dumps(
                        {
                            "error": f"Conflicting earning found: Another '{new_earning_type}' earning "
                            f"(ID: {other_id}) is already approved for employee '{employee_id}' in cycle '{cycle_id}'. "
                            "Cannot approve duplicate earnings of the same type for the same employee in the same cycle."
                        }
                    )

        # Apply updates
        if amount is not None:
            current_earning["amount"] = amount
        if earning_type is not None:
            current_earning["earning_type"] = earning_type
        if status is not None or new_status != current_earning.get("status"):
            current_earning["status"] = new_status

        timestamp = "2025-11-16T23:59:00"
        current_earning["last_updated"] = timestamp

        return json.dumps(current_earning)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_payroll_earning",
                "description": (
                    "Updates fields on an existing payroll earning record. "
                    "Can adjust the amount, change the earning type, and update the status. "
                    "High-value 'bonus' earnings over 5000 will be automatically marked with status "
                    "'require_justification' if not already approved or rejected. "
                    "When approving or rejecting earnings, the tool validates that no conflicting/duplicate "
                    "earnings of the same type exist for the same employee in the same cycle with 'approved' status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "earning_id": {
                            "type": "string",
                            "description": "ID of the payroll earning record to update (required).",
                        },
                        "amount": {
                            "type": "number",
                            "description": (
                                "Updated amount for the earning (optional). Must be a positive number."
                            ),
                        },
                        "status": {
                            "type": "string",
                            "description": (
                                "Updated status for the earning (optional). "
                                "Allowed values: 'pending', 'approved', 'rejected', 'require_justification'. "
                                "For 'bonus' earnings above 5000, the status will be automatically set to "
                                "'require_justification' unless explicitly approved or rejected."
                            ),
                        },
                        "earning_type": {
                            "type": "string",
                            "description": (
                                "Updated earning type (optional). "
                                "Allowed values: 'bonus', 'incentive', 'allowance', 'overtime'. "
                                "When set to 'bonus' with amount exceeding 5000, the status will require justification."
                            ),
                        },
                    },
                    "required": ["earning_id"],
                },
            },
        }
