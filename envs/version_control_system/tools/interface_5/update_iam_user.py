import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class UpdateIamUser(Tool):
    """
    Update an IAM user's status (suspend or reactivate).
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        status: str,
    ) -> str:
        """
        Update the status of an IAM user account.

        Parameters:
        - user_id (str, required): The unique identifier of the user to update.
        - status (str, required): The new status for the user. Must be one of: "active", "suspended".
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        users = data.get("users")

        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "users store missing"})

        # Validate user_id
        if not user_id or not isinstance(user_id, str):
            return json.dumps({"success": False, "error": "user_id is required and must be a string"})
        user_id = user_id.strip()

        if not user_id:
            return json.dumps({"success": False, "error": "user_id cannot be empty"})

        # Find user by user_id
        user = users.get(user_id)
        if not user:
            return json.dumps({"success": False, "error": f"User with user_id '{user_id}' not found"})

        # Validate status
        if not status or not isinstance(status, str):
            return json.dumps({"success": False, "error": "status is required and must be a string"})
        status = status.strip().lower()

        allowed_statuses = {"active", "suspended"}
        if status not in allowed_statuses:
            return json.dumps({
                "success": False,
                "error": f"status must be one of: {', '.join(sorted(allowed_statuses))}"
            })

        # Check if user is deleted - cannot update deleted users
        current_status = user.get("status", "").lower()
        if current_status == "deleted":
            return json.dumps({
                "success": False,
                "error": f"Cannot update user '{user_id}' because the account has been deleted"
            })

        # Check if status is already the same
        if current_status == status:
            return json.dumps({
                "success": False,
                "error": f"User '{user_id}' is already {status}"
            })

        # Update the user status
        timestamp = "2026-01-01T23:59:00"
        user["status"] = status
        user["updated_at"] = timestamp

        # Filter out unsupported fields
        filtered_user = {k: v for k, v in user.items() if k not in {"plan_type", "account_type", "two_factor_enabled"}}

        return json.dumps({
            "success": True,
            "message": f"User '{user_id}' status updated to '{status}'",
            "user": filtered_user
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_iam_user",
                "description": (
                    "Update an IAM user's status. Use this to suspend or reactivate a user account."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status for the user. Must be one of: active, suspended.",
                        },
                    },
                    "required": ["user_id", "status"],
                },
            },
        }
