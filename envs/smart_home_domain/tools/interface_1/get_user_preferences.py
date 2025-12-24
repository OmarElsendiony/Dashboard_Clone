import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetUserPreferences(Tool):
    """
    Retrieve user preferences including favorite devices.
    Returns all favorites associated with the user across all their homes.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_email: str,
    ) -> str:
        """
        Retrieves all user preferences (favorite devices) for a user.
        
        Args:
            data: The complete data dictionary containing all tables
            user_email: Email address of the user (required)
            
        Returns:
            JSON string with success status and user preferences or error message
        """

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        users = data.get("users", {})
        favorite_devices = data.get("user_home_favorite_devices", {})

        if not isinstance(users, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid users container: expected dict at data['users']",
                }
            )

        if not isinstance(favorite_devices, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid favorite_devices container: expected dict at data['user_home_favorite_devices']",
                }
            )

        # Validate required parameters
        if not user_email:
            return json.dumps(
                {"success": False, "error": "user_email is required"}
            )

        # Find user by email
        user_id = None
        user_email_str = str(user_email)
        
        for uid, user_data in users.items():
            if isinstance(user_data, dict) and user_data.get("email") == user_email_str:
                user_id = uid
                break
        
        if not user_id:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with email '{user_email}' not found",
                }
            )

        # Collect all favorite devices for this user
        user_favorite_devices = []
        for fav_id, fav_data in favorite_devices.items():
            if isinstance(fav_data, dict) and fav_data.get("user_id") == user_id:
                user_favorite_devices.append(fav_data)

        # Return the preferences
        preferences = {
            "user_id": user_id,
            "user_email": user_email_str,
            "favorite_devices": user_favorite_devices,
            "total_favorite_devices": len(user_favorite_devices),
        }

        return json.dumps({"success": True, "preferences": preferences})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "get_user_preferences",
                "description": (
                    "Retrieve user preferences including favorite devices. "
                    "Returns all favorites associated with the user across all their homes. "
                    "This is useful for quick access configuration and displaying user's preferred devices."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "Email address of the user (required).",
                        },
                    },
                    "required": ["user_email"],
                },
            },
        }

