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

        users = data.get("users", {})
        if user_email and username:
            user_info = next(
                (
                    user
                    for user in users.values()
                    if user.get("email") == user_email
                    and user.get("username") == username
                ),
                None,
            )
            if not user_info:
                return json.dumps({"success": False, "error": "User not found"})
        elif username and not user_email:
            user_info = next(
                (user for user in users.values() if user.get("username") == username),
                None,
            )

        elif not username and user_email:
            user_info = next(
                (user for user in users.values() if user.get("email") == user_email),
                None,
            )
        else:
            return json.dumps(
                {"success": False, "error": "user_email or username is required"}
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
                "description": "Retrieves information about a user in the version control system using the user's email address or username.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "The email address of the user to be retrieved.",
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
