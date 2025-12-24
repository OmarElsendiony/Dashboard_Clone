import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class GetSceneFavoritePreferences(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        household_id: str,
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

        favorite_scenes_dict = data.get("user_home_favorite_scenes", {})
        if not isinstance(favorite_scenes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid user_home_favorite_scenes container: expected dict at data['user_home_favorite_scenes']",
                }
            )

        # Type cast parameters to string as requested
        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required"})
        user_id_str = str(user_id).strip()

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})
        household_id_str = str(household_id).strip()

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

        # Validate favorite_name is not empty
        if len(favorite_name_str.strip()) == 0:
            return json.dumps(
                {"success": False, "error": "favorite_name cannot be empty"}
            )

        # Retrieve matching favorite preferences
        matching_favorites = []

        for preference_id, preference in favorite_scenes_dict.items():
            if not isinstance(preference, dict):
                continue

            pref_user_id = str(preference.get("user_id", ""))
            pref_home_id = str(preference.get("home_id", ""))
            pref_favorite_name = preference.get("favorite_name")

            # Check if this preference matches all criteria
            if (
                pref_user_id == user_id_str
                and pref_home_id == household_id_str
                and pref_favorite_name
                and str(pref_favorite_name) == favorite_name_str
            ):
                preference_copy = preference.copy()
                matching_favorites.append(preference_copy)

        # Sort by created_at for consistent ordering
        matching_favorites.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return json.dumps(
            {
                "success": True,
                "favorites": matching_favorites,
                "count": len(matching_favorites),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_scene_favorite_preferences",
                "description": (
                    "Retrieve scene favorite preferences for a user in a household. "
                    "Returns favorite scene preferences that match the specified user, household, and favorite name. "
                    "Each favorite preference includes preference_id, user_id, home_id, favorite_name, "
                    "scene_id (comma-separated if multiple scenes), created_at, and updated_at. "
                    "Returns an error if the user or household doesn't exist. "
                    "Returns empty list if no matching favorites are found."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user whose favorite preferences to retrieve.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household/home to filter favorites by.",
                        },
                        "favorite_name": {
                            "type": "string",
                            "description": "The name of the favorite to retrieve.",
                        },
                    },
                    "required": ["user_id", "household_id", "favorite_name"],
                },
            },
        }
