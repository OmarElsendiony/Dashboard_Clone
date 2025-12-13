import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class UpdatePayrollDeduction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        deduction_id: str,
        updates: Dict[str, Any],
    ) -> str:
        """
        Update an existing payroll deduction.
        
        Args:
            data: The database dictionary containing all tables.
            deduction_id: The ID of the deduction to update (required).
            updates: JSON object containing fields to update (required).
                Supported fields: amount, deduction_date, status.
                status allowed values: 'valid', 'invalid_limit_exceeded'.
        
        Returns:
            JSON string with the updated deduction record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not deduction_id:
            return json.dumps({"error": "Missing required parameter: deduction_id is required"})
        if not updates or not isinstance(updates, dict):
            return json.dumps({"error": "Missing required parameter: updates must be a JSON object"})

        deduction_id = str(deduction_id)
        deductions = data.get("deductions", {})

        if deduction_id not in deductions:
            return json.dumps({"error": f"Deduction with ID '{deduction_id}' not found"})

        deduction = deductions[deduction_id]

        # Validate status if being updated
        if "status" in updates:
            allowed_statuses = ["valid", "invalid_limit_exceeded"]
            if updates["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
                })

        # Allowed fields to update
        allowed_fields = ["amount", "deduction_date", "status"]

        for key, value in updates.items():
            if key in allowed_fields:
                deduction[key] = value

        deduction["last_updated"] = "2025-12-12T12:00:00"

        return json.dumps(deduction)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_payroll_deduction",
                "description": (
                    "Updates an existing payroll deduction with the provided fields. "
                    "Use this to modify deduction amounts, dates, or status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deduction_id": {
                            "type": "string",
                            "description": "The ID of the deduction to update (required).",
                        },
                        "updates": {
                            "type": "object",
                            "description": (
                                "JSON object containing fields to update (required). "
                                "Supported fields: amount, deduction_date, status."
                            ),
                            "properties": {
                                "amount": {
                                    "type": "number",
                                    "description": "The deduction amount.",
                                },
                                "deduction_date": {
                                    "type": "string",
                                    "description": "The deduction date in format (YYYY-MM-DD).",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The deduction status. Allowed values: 'valid', 'invalid_limit_exceeded'.",
                                },
                            },
                        },
                    },
                    "required": ["deduction_id", "updates"],
                },
            },
        }
