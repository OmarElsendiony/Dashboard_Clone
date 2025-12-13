import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class ApproveBonus(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        earning_id: str,
    ) -> str:
        """
        Approve a bonus earning.
        
        Args:
            data: The database dictionary containing all tables.
            earning_id: The ID of the bonus earning to approve (required).
        
        Returns:
            JSON string with the approved bonus earning record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not earning_id:
            return json.dumps({"error": "Missing required parameter: earning_id is required"})

        earning_id = str(earning_id)
        payroll_earnings = data.get("payroll_earnings", {})

        if earning_id not in payroll_earnings:
            return json.dumps({"error": f"Earning with ID '{earning_id}' not found"})

        earning = payroll_earnings[earning_id]
        
        if earning.get("earning_type") != "bonus":
            return json.dumps({"error": f"Earning '{earning_id}' is not a bonus"})

        if earning.get("status") == "approved":
            return json.dumps({"error": f"Bonus '{earning_id}' is already approved"})

        if earning.get("status") == "rejected":
            return json.dumps({"error": f"Cannot approve rejected bonus '{earning_id}'"})

        earning["status"] = "approved"
        earning["last_updated"] = "2025-12-12T12:00:00"

        return json.dumps(earning)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "approve_bonus",
                "description": (
                    "Approves a pending or require_justification bonus earning. "
                    "Cannot approve already rejected bonuses."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "earning_id": {
                            "type": "string",
                            "description": "The ID of the bonus earning to approve (required).",
                        },
                    },
                    "required": ["earning_id"],
                },
            },
        }
