import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateDeductionCodeStatus(Tool):
    """
    Update the status of a deduction code (deducation code).
    - Updates deducation code status (active, inactive).
    - Validates deducation code exists before updating.
    - Updates the last_updated timestamp.
    - Returns the updated deducation code details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        code_id: str,
        status: str,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "deduction_rule": {...}} on success
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

        deduction_rules_dict = data.get("deduction_rules", {})
        if not isinstance(deduction_rules_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid deduction_rules container: expected dict at data['deduction_rules']",
                }
            )

        # Validate code_id is provided
        if not code_id:
            return json.dumps({"success": False, "error": "code_id is required"})
        
        # Validate status is provided
        if not status:
            return json.dumps({"success": False, "error": "status is required"})

        # Convert code_id to string for consistent comparison
        code_id_str = str(code_id)

        # Check if deducation code exists
        if code_id_str not in deduction_rules_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Deduction rule with ID '{code_id_str}' not found",
                }
            )

        # Get the existing deducation code
        deduction_rule = deduction_rules_dict[code_id_str]
        if not isinstance(deduction_rule, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid deducation code data for ID '{code_id_str}'",
                }
            )

        # Validate status
        valid_statuses = ["active", "inactive"]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Update the deducation code status
        deduction_rule["status"] = status

        # Update timestamp
        deduction_rule["last_updated"] = "2025-11-16T23:59:00"

        return json.dumps(
            {
                "success": True,
                "code_id": deduction_rule,
                "message": f"Deduction code '{code_id_str}' status updated to '{status}'",
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
                "name": "update_deduction_code_status",
                "description": (
                    "Update the status of a deduction code (deducation code). "
                    "Valid statuses: active, inactive. "
                    "Updates the last_updated timestamp automatically. "
                    "Returns the updated deducation code details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code_id": {
                            "type": "string",
                            "description": "The ID of the deducation code to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "New status for the deducation code. Valid values: 'active', 'inactive'."
                        }
                    },
                    "required": ["code_id", "status"],
                },
            },
        }