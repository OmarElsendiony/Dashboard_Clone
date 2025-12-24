import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateDeviceFavoritePreferences(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        preference_id: str,
        device_id: Optional[str] = None,
        favorite_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
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

        if not preference_id:
            return json.dumps({"success": False, "error": "preference_id is required"})
        preference_id_str = str(preference_id).strip()

        if not favorite_name and not device_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one of favorite_name or device_id must be provided for update",
                }
            )

        # Check if preference exists
        if preference_id_str not in favorite_devices_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Preference with ID '{preference_id_str}' not found",
                }
            )

        preference = favorite_devices_dict[preference_id_str]

        # Get user_id and household_id from the existing preference
        current_user_id = str(preference.get("user_id", ""))
        current_household_id = str(preference.get("home_id", ""))

        # Handle favorite_name update if provided
        if favorite_name:
            favorite_name_str = str(favorite_name).strip()

            # Check for duplicate favorite_name (only if not empty)
            if len(favorite_name_str) > 0:
                # Check if another preference with same name exists for same user/household
                for pref_id, pref in favorite_devices_dict.items():
                    if not isinstance(pref, dict):
                        continue

                    # Skip the current preference being updated
                    if pref_id == preference_id_str:
                        continue

                    pref_user_id = str(pref.get("user_id", ""))
                    pref_household_id = str(pref.get("home_id", ""))
                    pref_favorite_name = pref.get("favorite_name")

                    # Check if duplicate exists
                    if (
                        pref_user_id == current_user_id
                        and pref_household_id == current_household_id
                        and pref_favorite_name
                        and str(pref_favorite_name).strip() == favorite_name_str
                    ):
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"A favorite with name '{favorite_name_str}' already exists for this user in this household",
                            }
                        )

                preference["favorite_name"] = favorite_name_str
            else:
                # Empty string means set to None
                return json.dumps(
                    {"success": False, "error": "favorite_name cannot be empty"}
                )

        # Handle device_id - append to existing if provided
        if device_id:
            device_id_str = str(device_id).strip()

            # Parse new device IDs
            new_device_ids = [d.strip() for d in device_id_str.split(",") if d.strip()]

            # Validate each new device exists
            for dev_id in new_device_ids:
                if dev_id not in devices_dict:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Device with ID '{dev_id}' not found",
                        }
                    )

            # Get existing device IDs
            existing_device_id = preference.get("device_id", "")
            existing_device_ids = []
            if existing_device_id:
                existing_device_ids = [
                    d.strip() for d in str(existing_device_id).split(",") if d.strip()
                ]

            # Combine existing and new device IDs (avoid duplicates)
            combined_device_ids = existing_device_ids.copy()
            for dev_id in new_device_ids:
                if dev_id not in combined_device_ids:
                    combined_device_ids.append(dev_id)

            # Update device_id as comma-separated without whitespaces
            preference["device_id"] = ",".join(combined_device_ids)

        # Update timestamp
        preference["updated_at"] = "2025-12-19T23:59:00"

        preference_return = preference.copy()
        preference_return["household_id"] = preference_return.pop("home_id")        

        return json.dumps(
            {
                "success": True,
                "preference_id": preference_id_str,
                "message": f"Device favorite preference '{preference_id_str}' updated successfully",
                "preference": preference_return,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_device_favorite_preferences",
                "description": (
                    "Update an existing device favorite preference. "
                    "If device_id is provided, appends new device IDs to existing ones as comma-separated values without whitespaces. "
                    "Duplicates are automatically removed. "
                    "If favorite_name is provided, updates the name of the favorite. "
                    "Validates that no duplicate favorite_name exists for the same user and household. "
                    "Validates that the preference exists and any new devices exist. "
                    "Returns the updated preference details on success. "
                    "Returns an error if validation fails or duplicate name is found."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "preference_id": {
                            "type": "string",
                            "description": "The ID of the preference to update.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Optional. Device ID or comma-separated device IDs to append to the existing favorites.",
                        },
                        "favorite_name": {
                            "type": "string",
                            "description": "Optional. A new name for this favorite preference.",
                        },
                    },
                    "required": ["preference_id"],
                },
            },
        }
