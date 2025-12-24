import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class SetUserPreferences(Tool):
    """
    Add or delete user preferences (favorite devices).
    Manages the user's favorite devices collection.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_email: str,
        preferred_item: str,
        action: str,
    ) -> str:
        """
        Adds or deletes a favorite device for a user.
        
        Args:
            data: The complete data dictionary containing all tables
            user_email: Email address of the user (required)
            preferred_item: Device ID to add/remove (required)
            action: Action to perform - 'add' or 'delete'/'remove' (required)
            
        Returns:
            JSON string with success status and operation result or error message
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            try:
                max_id = max(int(k) for k in table.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                return "1"

        # Fixed timestamp as per requirements
        timestamp = "2025-12-19T23:59:00"

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        users = data.get("users", {})
        devices = data.get("devices", {})
        favorite_devices = data.get("user_home_favorite_devices", {})

        if not isinstance(users, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid users container: expected dict at data['users']",
                }
            )

        # Validate required parameters
        if not user_email:
            return json.dumps(
                {"success": False, "error": "user_email is required"}
            )

        if not preferred_item:
            return json.dumps(
                {"success": False, "error": "preferred_item is required"}
            )

        if not action:
            return json.dumps(
                {"success": False, "error": "action is required"}
            )

        # Normalize and validate action
        action_lower = str(action).lower()
        if action_lower not in ["add", "delete", "remove"]:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action: '{action}'. Must be 'add', 'delete', or 'remove'",
                }
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

        preferred_item_str = str(preferred_item)

        # Validate device exists
        if preferred_item_str not in devices:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Device with ID '{preferred_item_str}' not found",
                }
            )

        device = devices[preferred_item_str]
        home_id = device.get("home_id")
        device_name = device.get("device_name", "")

        if action_lower == "add":
            # Check if already in favorites
            for fav_id, fav_data in favorite_devices.items():
                if (isinstance(fav_data, dict) and 
                    fav_data.get("user_id") == user_id and 
                    fav_data.get("device_id") == preferred_item_str):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Device '{preferred_item_str}' is already in user's favorites",
                        }
                    )

            # Add to favorites
            new_pref_id = generate_id(favorite_devices)
            new_favorite = {
                "preference_id": new_pref_id,
                "user_id": user_id,
                "home_id": home_id,
                "favorite_name": device_name,
                "device_id": preferred_item_str,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            favorite_devices[new_pref_id] = new_favorite

            return json.dumps({
                "success": True,
                "action": "added",
                "preference": new_favorite
            })

        else:  # delete or remove
            # Find and remove from favorites
            removed = False
            removed_pref = None
            for fav_id, fav_data in list(favorite_devices.items()):
                if (isinstance(fav_data, dict) and 
                    fav_data.get("user_id") == user_id and 
                    fav_data.get("device_id") == preferred_item_str):
                    removed_pref = fav_data.copy()
                    del favorite_devices[fav_id]
                    removed = True
                    break

            if not removed:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device '{preferred_item_str}' is not in user's favorites",
                    }
                )

            return json.dumps({
                "success": True,
                "action": "deleted",
                "preference": removed_pref
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_user_preferences",
                "description": (
                    "Add or delete user preferences (favorite devices). "
                    "Manages the user's favorite devices collection for quick access. "
                    "When adding, validates that the device exists. "
                    "When deleting, removes the device from favorites."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "Email address of the user (required).",
                        },
                        "preferred_item": {
                            "type": "string",
                            "description": "Device ID to add/remove from favorites (required).",
                        },
                        "action": {
                            "type": "string",
                            "description": "Action to perform - 'add' to add to favorites, 'delete' or 'remove' to remove from favorites (required).",
                        },
                    },
                    "required": ["user_email", "preferred_item", "action"],
                },
            },
        }

