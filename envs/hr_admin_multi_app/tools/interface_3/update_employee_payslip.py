import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class UpdateEmployeePayslip(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payslip_id: str,
        updates: Dict[str, Any],
    ) -> str:
        """
        Update an existing payslip status.
        
        Args:
            data: The database dictionary containing all tables.
            payslip_id: The ID of the payslip to update (required).
            updates: JSON object containing fields to update (required).
                Supported fields: status.
                status allowed values: 'draft', 'released', 'updated'.
        
        Returns:
            JSON string with the updated payslip record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not payslip_id:
            return json.dumps({"error": "Missing required parameter: payslip_id is required"})
        if not updates or not isinstance(updates, dict):
            return json.dumps({"error": "Missing required parameter: updates must be a JSON object"})

        # Validate that updates dict does not contain empty string keys
        for key in updates.keys():
            if not key or not isinstance(key, str) or key.strip() == "":
                return json.dumps({
                    "error": "Invalid updates: field names cannot be empty strings"
                })

        # Validate that updates dict does not contain empty string values
        for key, value in updates.items():
            if isinstance(value, str) and value.strip() == "":
                return json.dumps({
                    "error": f"Invalid updates: field '{key}' cannot have an empty string value"
                })

        payslip_id = str(payslip_id)
        payslips = data.get("payslips", {})

        if payslip_id not in payslips:
            return json.dumps({"error": f"Payslip with ID '{payslip_id}' not found"})

        payslip = payslips[payslip_id]

        # Allowed fields to update (net_pay_value is calculated internally, not updateable)
        allowed_fields = ["status"]

        # Check if any provided field is not allowed
        for key in updates.keys():
            if key not in allowed_fields:
                return json.dumps({
                    "error": f"Field '{key}' is not allowed to be updated. Only 'status' can be updated."
                })

        # Validate status if being updated
        if "status" in updates:
            allowed_statuses = ["draft", "released", "updated"]
            if updates["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
                })

        for key, value in updates.items():
            if key in allowed_fields:
                payslip[key] = value

        payslip["last_updated"] = "2025-12-12T12:00:00"

        return json.dumps(payslip)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_employee_payslip",
                "description": (
                    "Updates an existing payslip status. "
                    "Only the status field can be updated. "
                    "Net pay value is calculated internally and cannot be modified directly."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payslip_id": {
                            "type": "string",
                            "description": "The ID of the payslip to update (required).",
                        },
                        "updates": {
                            "type": "object",
                            "description": (
                                "JSON object containing fields to update (required). "
                                "Only 'status' field is supported."
                            ),
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "description": "The payslip status. Allowed values: 'draft', 'released', 'updated'.",
                                },
                            },
                        },
                    },
                    "required": ["payslip_id", "updates"],
                },
            },
        }
