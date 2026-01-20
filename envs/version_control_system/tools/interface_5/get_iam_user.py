import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetIamUser(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        users = data.get("users", {})

        # Search for user by email
        for _, user in users.items():
            if user.get("email") == email:
                user_data = {
                    k: v for k, v in user.items()
                    if k not in ("account_type", "plan_type", "two_factor_enabled")
                }
                return json.dumps({
                    "success": True,
                    "user_data": user_data
                })

        return json.dumps({
            "success": False,
            "error": f"User with email '{email}' not found"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_iam_user",
                "description": "Retrieves IAM user information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "The email address of the user to look up. Required field.",
                        },
                    },
                    "required": ["email"],
                },
            },
        }
