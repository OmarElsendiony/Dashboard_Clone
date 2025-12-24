import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ToggleFavoriteDevice(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        device_id: str,
        action: str
    ) -> str:
        """
        Toggle a device as favorite or unfavorite for users in a home.
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        user_home_favorite_devices_dict = data.get("user_home_favorite_devices", {})
        if not isinstance(user_home_favorite_devices_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid user_home_favorite_devices container: expected dict at data['user_home_favorite_devices']"
            })

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid devices container: expected dict at data['devices']"
            })

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid homes container: expected dict at data['homes']"
            })

        users_dict = data.get("users", {})
        if not isinstance(users_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid users container: expected dict at data['users']"
            })

        home_users_dict = data.get("home_users", {})
        if not isinstance(home_users_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid home_users container: expected dict at data['home_users']"
            })

        # Validate required parameters
        if not home_id:
            return json.dumps({
                "success": False,
                "error": "home_id is required"
            })

        if not device_id:
            return json.dumps({
                "success": False,
                "error": "device_id is required"
            })

        if not action:
            return json.dumps({
                "success": False,
                "error": "action is required"
            })

        home_id_str = str(home_id).strip()
        device_id_str = str(device_id).strip()
        action_str = str(action).strip().lower()

        # Validate action
        if action_str not in ["favorite", "unfavorite"]:
            return json.dumps({
                "success": False,
                "error": "action must be 'favorite' or 'unfavorite'"
            })

        # Validate home exists
        if home_id_str not in homes_dict:
            return json.dumps({
                "success": False,
                "error": f"Home with ID '{home_id_str}' not found"
            })

        # Validate device exists and belongs to the home
        if device_id_str not in devices_dict:
            return json.dumps({
                "success": False,
                "error": f"Device with ID '{device_id_str}' not found"
            })

        device_info = devices_dict[device_id_str]
        if not isinstance(device_info, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid device data for ID '{device_id_str}'"
            })

        if str(device_info.get("home_id")) != home_id_str:
            return json.dumps({
                "success": False,
                "error": f"Device '{device_id_str}' does not belong to home '{home_id_str}'"
            })

        device_name = device_info.get("device_name", "Unknown Device")
        device_type = device_info.get("device_type", "unknown")

        # Get all users in the home
        users_in_home = []
        for hu_id, home_user in home_users_dict.items():
            if not isinstance(home_user, dict):
                continue
            if str(home_user.get("home_id")) == home_id_str:
                user_id = str(home_user.get("user_id"))
                if user_id in users_dict:
                    users_in_home.append(user_id)

        if not users_in_home:
            return json.dumps({
                "success": False,
                "error": f"No users found in home '{home_id_str}'"
            })

        timestamp = "2025-12-19T23:59:00"
        results = []

        if action_str == "favorite":
            # Generate new preference_id
            numeric_ids = []
            for key in user_home_favorite_devices_dict.keys():
                try:
                    numeric_ids.append(int(key))
                except (TypeError, ValueError):
                    continue

            # Create favorite entries for each user in the home
            for user_id in users_in_home:
                # Check if favorite already exists for this user, home, and device
                existing_favorite = None
                for pref_id, favorite in user_home_favorite_devices_dict.items():
                    if not isinstance(favorite, dict):
                        continue
                    if (str(favorite.get("user_id")) == user_id and
                        str(favorite.get("home_id")) == home_id_str and
                        str(favorite.get("device_id")) == device_id_str):
                        existing_favorite = pref_id
                        break

                if existing_favorite:
                    # Update existing favorite
                    favorite_entry = user_home_favorite_devices_dict[existing_favorite]
                    favorite_entry["updated_at"] = timestamp
                    results.append({
                        "user_id": user_id,
                        "action": "updated",
                        "preference_id": existing_favorite
                    })
                else:
                    # Create new favorite
                    new_pref_id = str(max(numeric_ids, default=0) + 1)
                    numeric_ids.append(int(new_pref_id))

                    user_info = users_dict[user_id]
                    user_first_name = user_info.get("first_name", "Unknown")
                    user_last_name = user_info.get("last_name", "")

                    favorite_name = f"{device_name}"
                    if device_type == "door_lock":
                        favorite_name = "Front Door Lock"
                    elif device_type in ["bulb", "power_outlet"]:
                        favorite_name = "Bedroom Light" if "bedroom" in device_name.lower() else "Kitchen Speaker"
                    elif device_type in ["thermostat", "air_conditioner"]:
                        favorite_name = "Thermostat"
                    elif device_type == "camera":
                        favorite_name = "Main Camera"

                    new_favorite = {
                        "preference_id": new_pref_id,
                        "user_id": user_id,
                        "home_id": home_id_str,
                        "favorite_name": favorite_name,
                        "device_id": device_id_str,
                        "created_at": timestamp,
                        "updated_at": timestamp,
                        "preference_description": f"{user_first_name} {user_last_name}'s favorite: {favorite_name} ({device_type.replace('_', ' ').title()} {device_id_str})"
                    }

                    user_home_favorite_devices_dict[new_pref_id] = new_favorite
                    results.append({
                        "user_id": user_id,
                        "action": "created",
                        "preference_id": new_pref_id
                    })

        elif action_str == "unfavorite":
            # Remove favorite entries for all users in the home for this device
            favorites_to_remove = []
            for pref_id, favorite in user_home_favorite_devices_dict.items():
                if not isinstance(favorite, dict):
                    continue
                if (str(favorite.get("home_id")) == home_id_str and
                    str(favorite.get("device_id")) == device_id_str):
                    user_id = str(favorite.get("user_id"))
                    if user_id in users_in_home:
                        favorites_to_remove.append(pref_id)
                        results.append({
                            "user_id": user_id,
                            "action": "removed",
                            "preference_id": pref_id
                        })

            # Remove from dictionary
            for pref_id in favorites_to_remove:
                del user_home_favorite_devices_dict[pref_id]

            if not results:
                return json.dumps({
                    "success": False,
                    "error": f"No favorite entries found for device '{device_id_str}' in home '{home_id_str}'"
                })

        return json.dumps({
            "success": True,
            "home_id": home_id_str,
            "device_id": device_id_str,
            "device_name": device_name,
            "action": action_str,
            "results": results,
            "message": f"Device '{device_name}' {action_str}d successfully"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "toggle_favorite_device",
                "description": "Toggle a device as favorite or unfavorite for all users in a home. For 'favorite' action, creates or updates favorite entries for all users in the home. For 'unfavorite' action, removes favorite entries for all users in the home. Validates that the home and device exist, and that the device belongs to the home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home."
                        },
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to toggle as favorite/unfavorite."
                        },
                        "action": {
                            "type": "string",
                            "description": "The action to perform: 'favorite' or 'unfavorite'."
                        }
                    },
                    "required": ["home_id", "device_id", "action"]
                }
            }
        }
