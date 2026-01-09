import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ListAccessToken(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
    ) -> str:
        """ Returns the access token for a specific user. """
        # Validate data structure and required containers
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})
        
        access_tokens_dict = data.get("access_tokens", {})
        users_dict = data.get("users", {})
        
        if not isinstance(access_tokens_dict, dict) or not isinstance(users_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data containers: 'access_tokens' and 'users' must be dicts"
            })

        # Validate required parameters
        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required"})

        user_id_str = str(user_id).strip()

        # Validate user exists
        user_info = users_dict.get(user_id_str)
        if not user_info or not isinstance(user_info, dict):
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id_str}' not found"
            })

        # Validate user is active
        if str(user_info.get("status", "")).strip() != "active":
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id_str}' is not active (status: {user_info.get('status')})"
            })

        # Find the access token for this user (single token per user)
        access_token = None
        for token_id, token in access_tokens_dict.items():
            if isinstance(token, dict) and str(token.get("user_id")) == user_id_str:
                access_token = {**token, "token_id": str(token_id)}
                break

        if not access_token:
            return json.dumps({
                "success": False,
                "error": f"No access token found for user '{user_info.get('username')}'"
            })
        
        return_access_token = access_token.copy()
        return_access_token.pop("token_encoded")

        return json.dumps({
            "success": True,
            "access_token": return_access_token,
            "message": f"Access token retrieved successfully for user '{user_info.get('username')}'",
            "username": user_info.get("username"),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """ Return tool metadata for the list_access_token function. """
        return {
            "type": "function",
            "function": {
                "name": "list_access_token",
                "description": (
                    "Retrieve the access token associated with a specific user. "
                    "Each user has exactly one access token. "
                    "Returns the access token including token_id, token_name, user_id, "
                    "status (active/revoked/expired), last_used_at, expires_at, created_at timestamps. "
                    "Validates that the user exists and is active. "
                    "Returns an error if the user doesn't exist, is not active, or has no access token."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user whose access token to retrieve.",
                        },
                    },
                    "required": ["user_id"],
                },
            },
        }
