import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateSceneFavoritePreferences(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        preference_id: str,
        scene_id: Optional[str] = None,
        favorite_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        scenes_dict = data.get("scenes", {})
        if not isinstance(scenes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid scenes container: expected dict at data['scenes']",
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

        # Type cast preference_id to string as requested
        if not preference_id:
            return json.dumps({"success": False, "error": "preference_id is required"})
        preference_id_str = str(preference_id).strip()

        if not favorite_name and not scene_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one of favorite_name or scene_id must be provided for update",
                }
            )

        # Check if preference exists
        if preference_id_str not in favorite_scenes_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Preference with ID '{preference_id_str}' not found",
                }
            )

        preference = favorite_scenes_dict[preference_id_str]

        # Get user_id and household_id from the existing preference
        current_user_id = str(preference.get("user_id", ""))
        current_household_id = str(preference.get("home_id", ""))

        # Handle favorite_name update if provided
        if favorite_name:
            favorite_name_str = str(favorite_name).strip()

            # Check for duplicate favorite_name (only if not empty)
            if len(favorite_name_str) > 0:
                # Check if another preference with same name exists for same user/household
                for pref_id, pref in favorite_scenes_dict.items():
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

        # Handle scene_id - append to existing if provided
        if scene_id:
            scene_id_str = str(scene_id).strip()

            # Parse new scene IDs
            new_scene_ids = [s.strip() for s in scene_id_str.split(",") if s.strip()]

            # Validate each new scene exists
            for scn_id in new_scene_ids:
                if scn_id not in scenes_dict:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Scene with ID '{scn_id}' not found",
                        }
                    )

            # Get existing scene IDs
            existing_scene_id = preference.get("scene_id", "")
            existing_scene_ids = []
            if existing_scene_id:
                existing_scene_ids = [
                    s.strip() for s in str(existing_scene_id).split(",") if s.strip()
                ]

            # Combine existing and new scene IDs (avoid duplicates)
            combined_scene_ids = existing_scene_ids.copy()
            for scn_id in new_scene_ids:
                if scn_id not in combined_scene_ids:
                    combined_scene_ids.append(scn_id)

            # Update scene_id as comma-separated without whitespaces
            preference["scene_id"] = ",".join(combined_scene_ids)

        # Update timestamp
        preference["updated_at"] = "2025-12-19T23:59:00"

        return json.dumps(
            {
                "success": True,
                "preference_id": preference_id_str,
                "message": f"Scene favorite preference '{preference_id_str}' updated successfully",
                "preference": preference,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_scene_favorite_preferences",
                "description": (
                    "Update an existing scene favorite preference. "
                    "If scene_id is provided, appends new scene IDs to existing ones as comma-separated values without whitespaces. "
                    "Duplicates are automatically removed. "
                    "If favorite_name is provided, updates the name of the favorite. "
                    "Validates that no duplicate favorite_name exists for the same user and household. "
                    "Validates that the preference exists and any new scenes exist. "
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
                        "scene_id": {
                            "type": "string",
                            "description": "Optional. Scene ID or comma-separated scene IDs to append to the existing favorites.",
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
