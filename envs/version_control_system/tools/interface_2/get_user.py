import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool

class GetUser(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        
        def validate_data_structure(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
            
            if not isinstance(data, dict):
                return False, "Invalid data format: 'data' must be a dict", None

            users_dict = data.get("users", {})
            if not isinstance(users_dict, dict):
                return False, "Invalid users container: expected dict at data['users']", None

            return True, None, users_dict

        def find_user_by_field(users_dict: Dict[str, Any], field: str, value: str) -> Optional[Dict[str, Any]]:
            """Find a user by a specific field and value."""
            for uid, user in users_dict.items():
                if not isinstance(user, dict):
                    continue
                
                if str(user.get(field, "")).strip() == value:
                    user_info = user.copy()
                    user_info["user_id"] = str(uid)
                    return user_info
            
            return None

        # Validate data structure
        is_valid, error_msg, users_dict = validate_data_structure(data)
        if not is_valid:
            return json.dumps({"success": False, "error": error_msg})

        # Validate that at least one parameter is provided
        if not username and not email:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one of username or email must be provided",
                }
            )

        # Convert to strings for consistent comparison
        username_str = str(username).strip() if username else None
        email_str = str(email).strip() if email else None

        # Search for user (username takes priority)
        result_user = None
        if username_str:
            result_user = find_user_by_field(users_dict, "username", username_str)
        elif email_str:
            result_user = find_user_by_field(users_dict, "email", email_str)
        
        if result_user is None:
            search_field = f"username '{username_str}'" if username_str else f"email '{email_str}'"
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with {search_field} not found",
                }
            )

        result_user.pop("account_type", None)
        return json.dumps(
            {
                "success": True,
                "user": result_user,
                "message": f"User '{result_user.get('username')}' retrieved successfully",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """ Returns tool metadata for get_user function. """
        return {
            "type": "function",
            "function": {
                "name": "get_user",
                "description": (
                    "Retrieve user details using a username or email (at least one required). If both are provided, the username is used first. Returns full user information, or an error if no input is given or the user does not exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Optional. The username of the user to retrieve.",
                        },
                        "email": {
                            "type": "string",
                            "description": "Optional. The email of the user to retrieve.",
                        },
                    },
                    "required": [],
                },
            },
        }