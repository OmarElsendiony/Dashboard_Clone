import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ResolveUserIdentity(Tool):

    @staticmethod
    def invoke(data: Dict[str, Any], user_email: str) -> str:
        """
        Retrieves user account information by their email address in the version control system.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not user_email:
            return json.dumps({"success": False, "error": "user_email is required to resolve user identity"})

        users = data.get("users", {})

        # Search for user by email
        found_user = None
        for user_id, user in users.items():
            if user.get("email") == user_email:
                found_user = user
                break

        if not found_user:
            return json.dumps({"success": False, "error": f"User with email '{user_email}' not found in the system"})

        return json.dumps({"success": True, "result": found_user})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_user_identity",
                "description": "Retrieves a user's account information from the version control system by looking up their email address.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "The email address of the user to look up in the version control system."
                        }
                    },
                    "required": ["user_email"]
                }
            }
        }
