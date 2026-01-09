import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class RetrieveUser(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        if not user_email and not username:
            return json.dumps(
                {"success": False, "error": "user_email or username is required"}
            )
        users = data.get("users", {})
        user_info = next(
            (
                user
                for user in users.values()
                if user.get("email") == user_email or user.get("username") == username
            ),
            None,
        )
        if not user_info:
            return json.dumps({"success": False, "error": "User not found"})
        return json.dumps({"success": True, "user": user_info})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_user",
                "description": "Retrieves information about a user in the version control system. One of username or user_email is required to fetch the user profile.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "The email address of the user to be retrieved on the system.",
                        },
                        "username": {
                            "type": "string",
                            "description": "The username of the user to be retrieved.",
                        },
                    },
                    "required": [],
                },
            },
        }
