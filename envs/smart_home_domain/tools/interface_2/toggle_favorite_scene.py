import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ToggleFavoriteScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        scene_id: str,
        action: str
    ) -> str:
        """
        Toggle a scene as favorite or unfavorite for users in a home.
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        user_home_favorite_scenes_dict = data.get("user_home_favorite_scenes", {})
        if not isinstance(user_home_favorite_scenes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid user_home_favorite_scenes container: expected dict at data['user_home_favorite_scenes']"
            })

        scenes_dict = data.get("scenes", {})
        if not isinstance(scenes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid scenes container: expected dict at data['scenes']"
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

        if not scene_id:
            return json.dumps({
                "success": False,
                "error": "scene_id is required"
            })

        if not action:
            return json.dumps({
                "success": False,
                "error": "action is required"
            })

        home_id_str = str(home_id).strip()
        scene_id_str = str(scene_id).strip()
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

        # Validate scene exists and belongs to the home
        if scene_id_str not in scenes_dict:
            return json.dumps({
                "success": False,
                "error": f"Scene with ID '{scene_id_str}' not found"
            })

        scene_info = scenes_dict[scene_id_str]
        if not isinstance(scene_info, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid scene data for ID '{scene_id_str}'"
            })

        if str(scene_info.get("home_id")) != home_id_str:
            return json.dumps({
                "success": False,
                "error": f"Scene '{scene_id_str}' does not belong to home '{home_id_str}'"
            })

        scene_name = scene_info.get("scene_name", "Unknown Scene")

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
            for key in user_home_favorite_scenes_dict.keys():
                try:
                    numeric_ids.append(int(key))
                except (TypeError, ValueError):
                    continue

            # Create favorite entries for each user in the home
            for user_id in users_in_home:
                # Check if favorite already exists for this user, home, and scene
                existing_favorite = None
                for pref_id, favorite in user_home_favorite_scenes_dict.items():
                    if not isinstance(favorite, dict):
                        continue
                    if (str(favorite.get("user_id")) == user_id and
                        str(favorite.get("home_id")) == home_id_str and
                        str(favorite.get("scene_id")) == scene_id_str):
                        existing_favorite = pref_id
                        break

                if existing_favorite:
                    # Update existing favorite
                    favorite_entry = user_home_favorite_scenes_dict[existing_favorite]
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

                    # Determine favorite_name based on scene name patterns
                    favorite_name = scene_name
                    if "morning" in scene_name.lower():
                        favorite_name = "Good Morning"
                    elif "evening" in scene_name.lower() or "night" in scene_name.lower():
                        favorite_name = "Movie Time"
                    elif "away" in scene_name.lower():
                        favorite_name = "Away Mode"

                    new_favorite = {
                        "preference_id": new_pref_id,
                        "user_id": user_id,
                        "home_id": home_id_str,
                        "favorite_name": favorite_name,
                        "scene_id": scene_id_str,
                        "created_at": timestamp,
                        "updated_at": timestamp,
                        "preference_description": f"{user_first_name} {user_last_name}'s favorite: {favorite_name} ({scene_name})"
                    }

                    user_home_favorite_scenes_dict[new_pref_id] = new_favorite
                    results.append({
                        "user_id": user_id,
                        "action": "created",
                        "preference_id": new_pref_id
                    })

        elif action_str == "unfavorite":
            # Remove favorite entries for all users in the home for this scene
            favorites_to_remove = []
            for pref_id, favorite in user_home_favorite_scenes_dict.items():
                if not isinstance(favorite, dict):
                    continue
                if (str(favorite.get("home_id")) == home_id_str and
                    str(favorite.get("scene_id")) == scene_id_str):
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
                del user_home_favorite_scenes_dict[pref_id]

            if not results:
                return json.dumps({
                    "success": False,
                    "error": f"No favorite entries found for scene '{scene_id_str}' in home '{home_id_str}'"
                })

        return json.dumps({
            "success": True,
            "home_id": home_id_str,
            "scene_id": scene_id_str,
            "scene_name": scene_name,
            "action": action_str,
            "results": results,
            "message": f"Scene '{scene_name}' {action_str}d successfully"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "toggle_favorite_scene",
                "description": "Toggle a scene as favorite or unfavorite for all users in a home. For 'favorite' action, creates or updates favorite entries for all users in the home. For 'unfavorite' action, removes favorite entries for all users in the home. Validates that the home and scene exist, and that the scene belongs to the home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home."
                        },
                        "scene_id": {
                            "type": "string",
                            "description": "The ID of the scene to toggle as favorite/unfavorite."
                        },
                        "action": {
                            "type": "string",
                            "description": "The action to perform: 'favorite' or 'unfavorite'."
                        }
                    },
                    "required": ["home_id", "scene_id", "action"]
                }
            }
        }
