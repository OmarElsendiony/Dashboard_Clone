import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateNewScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        scene_name: str,
        created_by_user_id: str,
        description: Optional[str] = None,
        voice_control_phrase: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Create a new scene for a home.
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
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

        # Validate required parameters
        if not home_id:
            return json.dumps({
                "success": False,
                "error": "home_id is required"
            })

        if not scene_name:
            return json.dumps({
                "success": False,
                "error": "scene_name is required"
            })

        if not created_by_user_id:
            return json.dumps({
                "success": False,
                "error": "created_by_user_id is required"
            })

        home_id_str = str(home_id).strip()
        scene_name_str = str(scene_name).strip()
        created_by_user_id_str = str(created_by_user_id).strip()

        # Validate home exists
        if home_id_str not in homes_dict:
            return json.dumps({
                "success": False,
                "error": f"Home with ID '{home_id_str}' not found"
            })

        # Validate user exists
        if created_by_user_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{created_by_user_id_str}' not found"
            })

        # Check for unique scene_name within the home (based on unique index)
        for sid, scene in scenes_dict.items():
            if not isinstance(scene, dict):
                continue
            if (str(scene.get("home_id")) == home_id_str and 
                str(scene.get("scene_name", "")).strip().lower() == scene_name_str.lower()):
                return json.dumps({
                    "success": False,
                    "error": f"Scene with name '{scene_name_str}' already exists in home '{home_id_str}'"
                })

        # Validate status if provided
        if status and status not in ["enabled", "disabled"]:
            return json.dumps({
                "success": False,
                "error": "status must be one of: 'enabled', 'disabled'"
            })

        # Generate new scene_id
        numeric_ids = []
        for key in scenes_dict.keys():
            try:
                numeric_ids.append(int(key))
            except (TypeError, ValueError):
                continue
        new_scene_id = str(max(numeric_ids, default=0) + 1)

        # Set default status
        scene_status = status if status else "enabled"
        timestamp = "2025-12-19T23:59:00"

        # Create new scene record
        new_scene = {
            "scene_id": new_scene_id,
            "home_id": home_id_str,
            "created_by_user_id": created_by_user_id_str,
            "scene_name": scene_name_str,
            "description": description.strip() if description and isinstance(description, str) else None,
            "status": scene_status,
            "voice_control_phrase": voice_control_phrase.strip() if voice_control_phrase and isinstance(voice_control_phrase, str) else None,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        # Add to data
        scenes_dict[new_scene_id] = new_scene

        return json.dumps({
            "success": True,
            "scene": new_scene
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_scene",
                "description": "Create a new scene for a home. Validates that the home and user exist, and ensures scene name is unique within the home. Returns the created scene with generated scene_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home to create the scene for."
                        },
                        "scene_name": {
                            "type": "string",
                            "description": "The name of the scene. Must be unique within the home."
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the scene."
                        },
                        "voice_control_phrase": {
                            "type": "string",
                            "description": "Optional voice control phrase for the scene."
                        },
                        "created_by_user_id": {
                            "type": "string",
                            "description": "The ID of the user creating the scene."
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status: 'enabled' or 'disabled'. Defaults to 'enabled'."
                        }
                    },
                    "required": ["home_id", "scene_name", "created_by_user_id"]
                }
            }
        }