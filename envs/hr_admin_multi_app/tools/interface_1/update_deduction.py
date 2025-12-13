import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class UpdateDeduction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        deduction_id: str,
        deduction_rule_id: Optional[str] = None,
        amount: Optional[float] = None,
        deduction_date: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """Update deduction_rule_id, amount, deduction_date, or status for a deduction record."""

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        deductions = data.get("deductions", {})
        if not isinstance(deductions, dict):
            return json.dumps({"success": False, "error": "Invalid deductions structure"})

        if not isinstance(deduction_id, str) or not deduction_id.strip():
            return json.dumps({"success": False, "error": "deduction_id must be a non-empty string"})
        deduction_id = deduction_id.strip()

        record = deductions.get(deduction_id)
        if not isinstance(record, dict):
            return json.dumps({"success": False, "error": "Deduction not found"})

        update_fields: Dict[str, Any] = {}

        if deduction_rule_id is not None:
            if not isinstance(deduction_rule_id, str) or not deduction_rule_id.strip():
                return json.dumps({"success": False, "error": "deduction_rule_id must be a non-empty string"})
            update_fields["deduction_rule_id"] = deduction_rule_id.strip()

        if amount is not None:
            if not isinstance(amount, (int, float)) or amount <= 0:
                return json.dumps({"success": False, "error": "amount must be a positive number"})
            update_fields["amount"] = round(float(amount), 2)

        if deduction_date is not None:
            if not isinstance(deduction_date, str) or not deduction_date.strip():
                return json.dumps({"success": False, "error": "deduction_date must be a non-empty string"})
            update_fields["deduction_date"] = deduction_date.strip()

        if status is not None:
            valid_status = {"valid", "invalid_limit_exceeded"}
            if status not in valid_status:
                return json.dumps({"success": False, "error": "Invalid status"})
            update_fields["status"] = status

        if not update_fields:
            return json.dumps({"success": False, "error": "No valid fields provided for update"})

        timestamp = "2025-11-22T12:00:00"
        record.update(update_fields)
        record["last_updated"] = timestamp

        return json.dumps(
            {
                "success": True,
                "message": "Payroll deduction updated",
                "payroll_deduction": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_deduction",
                "description": "Update deduction_rule_id, amount, deduction_date, or status for an existing deduction.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deduction_id": {"type": "string", "description": "Identifier of the deduction to update."},
                        "deduction_rule_id": {
                            "type": "string",
                            "description": "(Optional) Replacement deduction_rule_id value.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "New deduction amount (must be positive decimal).",
                        },
                        "deduction_date": {"type": "string", "description": "New deduction date (YYYY-MM-DD)."},
                        "status": {
                            "type": "string",
                            "description": "Lifecycle status to set (allowed values: valid, invalid_limit_exceeded).",
                        },
                    },
                    "required": ["deduction_id"],
                },
            },
        }
