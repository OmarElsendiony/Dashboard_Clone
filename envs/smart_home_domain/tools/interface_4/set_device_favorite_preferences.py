import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class SetDeviceFavoritePreferences(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        device_id: str,
        household_id: str,
        user_id: str,
        favorite_name: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        users_dict = data.get("users", {})
        if not isinstance(users_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid users container: expected dict at data['users']",
                }
            )

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid homes container: expected dict at data['homes']",
                }
            )

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid devices container: expected dict at data['devices']",
                }
            )

        favorite_devices_dict = data.get("user_home_favorite_devices", {})
        if not isinstance(favorite_devices_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid user_home_favorite_devices container: expected dict at data['user_home_favorite_devices']",
                }
            )

        # Type cast parameters to string as requested
        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required"})
        user_id_str = str(user_id).strip()

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})
        household_id_str = str(household_id).strip()

        if not device_id:
            return json.dumps({"success": False, "error": "device_id is required"})
        device_id_str = str(device_id).strip()

        if not favorite_name:
            return json.dumps({"success": False, "error": "favorite_name is required"})
        favorite_name_str = str(favorite_name).strip()

        # Validate user exists
        if user_id_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{user_id_str}' not found",
                }
            )

        # Validate household exists
        if household_id_str not in homes_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Household with ID '{household_id_str}' not found",
                }
            )

        # Parse and validate device_id(s) - can be comma-separated
        device_ids = [d.strip() for d in device_id_str.split(",") if d.strip()]

        if not device_ids:
            return json.dumps(
                {"success": False, "error": "At least one device_id must be provided"}
            )

        # Validate each device exists
        for dev_id in device_ids:
            if dev_id not in devices_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device with ID '{dev_id}' not found",
                    }
                )

        # Create comma-separated device_id string without whitespaces
        device_id_combined = ",".join(device_ids)

        # Generate unique preference_id
        # Generate new IDs
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        preference_id = generate_id(favorite_devices_dict)

        # Create timestamp
        created_at = "2025-12-19T23:59:00"

        # Create new favorite preference entry
        new_preference = {
            "preference_id": preference_id,
            "user_id": user_id_str,
            "home_id": household_id_str,
            "favorite_name": favorite_name_str,
            "device_id": device_id_combined,
            "created_at": created_at,
            "updated_at": created_at,
        }

        # Add to data structure
        favorite_devices_dict[preference_id] = new_preference

        new_preference_return = new_preference.copy()
        new_preference_return["household_id"] = new_preference_return.pop("home_id")

        message = (
            f"Device favorite preference created successfully for user '{user_id_str}'"
        )
        if favorite_name_str:
            message += f" with name '{favorite_name_str}'"

        return json.dumps(
            {
                "success": True,
                "preference_id": preference_id,
                "message": message,
                "data": new_preference_return,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_device_favorite_preferences",
                "description": (
                    "Create a new device favorite preference for a user. "
                    "Creates a favorite preference with specified device(s). "
                    "Validates that the user, household, and device(s) exist. "
                    "Supports single device ID or multiple device IDs (comma-separated). "
                    "Returns the created preference_id on success. "
                    "Returns an error if validation fails."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The device ID or comma-separated device IDs to add to favorites.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user creating the favorite preference.",
                        },
                        "favorite_name": {
                            "type": "string",
                            "description": "A name for this favorite preference.",
                        },
                    },
                    "required": [
                        "device_id",
                        "household_id",
                        "user_id",
                        "favorite_name",
                    ],
                },
            },
        }