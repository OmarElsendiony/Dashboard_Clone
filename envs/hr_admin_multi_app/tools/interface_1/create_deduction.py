import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateDeduction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        deduction_rule_id: str,
        amount: float,
        deduction_date: str,
        status: str = "valid",
    ) -> str:
        """Create a deduction record tied to an existing deduction rule."""

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        deductions = data.setdefault("deductions", {})
        if not isinstance(deductions, dict):
            return json.dumps({"success": False, "error": "Invalid deductions structure"})

        def require_str(value: Optional[str], field: str) -> str:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
            return value.strip()

        try:
            employee_id = require_str(employee_id, "employee_id")
            deduction_rule_id = require_str(deduction_rule_id, "deduction_rule_id")
            deduction_date = require_str(deduction_date, "deduction_date")
        except ValueError as exc:
            return json.dumps({"success": False, "error": str(exc)})

        if not isinstance(amount, (int, float)) or amount <= 0:
            return json.dumps({"success": False, "error": "amount must be a positive number"})
        amount = round(float(amount), 2)

        valid_status = {"valid", "invalid_limit_exceeded"}
        if status not in valid_status:
            return json.dumps({"success": False, "error": "Invalid status"})

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            numeric_ids = [int(k) for k in table.keys() if str(k).isdigit()]
            return str(max(numeric_ids, default=0) + 1)

        deduction_id = generate_id(deductions)
        timestamp = "2025-11-22T12:00:00"
        record = {
            "deduction_id": deduction_id,
            "employee_id": employee_id,
            "deduction_rule_id": deduction_rule_id,
            "amount": amount,
            "deduction_date": deduction_date,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        deductions[deduction_id] = record

        return json.dumps(
            {
                "success": True,
                "message": "Payroll deduction created",
                "payroll_deduction": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_deduction",
                "description": "Create a deduction record linked to a deduction rule.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee id for whom the deduction is created.",
                        },
                        "deduction_rule_id": {
                            "type": "string",
                            "description": "Reference to the deduction rule this entry follows.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "Positive deduction amount stored as decimal.",
                        },
                        "deduction_date": {
                            "type": "string",
                            "description": "Date the deduction applies (YYYY-MM-DD).",
                        },
                        "status": {
                            "type": "string",
                            "description": "Lifecycle status (default valid; allowed values: valid, invalid_limit_exceeded).",
                        },
                    },
                    "required": [
                        "employee_id",
                        "deduction_rule_id",
                        "amount",
                        "deduction_date",
                    ],
                },
            },
        }
