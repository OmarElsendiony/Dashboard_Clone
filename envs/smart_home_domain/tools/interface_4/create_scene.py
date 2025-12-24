import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scene_name: str,
        status: str,
        household_id: str,
        created_by_user_id: str,
        description: Optional[str] = None,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

        # Basic input validation
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

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid homes container: expected dict at data['homes']",
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

        # Validate required parameters
        if not scene_name:
            return json.dumps({"success": False, "error": "scene_name is required"})

        if not status:
            return json.dumps({"success": False, "error": "status is required"})

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        if not created_by_user_id:
            return json.dumps(
                {"success": False, "error": "created_by_user_id is required"}
            )

        # Convert to strings for consistent comparison
        scene_name_str = str(scene_name).strip()
        status_str = str(status).strip()
        description_str = str(description).strip() if description else ""
        household_id_str = str(household_id).strip()
        created_by_user_id_str = str(created_by_user_id).strip()

        # Validate status
        valid_statuses = ["enabled", "disabled"]
        if status_str not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
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

        home_info = homes_dict[household_id_str]
        if not isinstance(home_info, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid household data for ID '{household_id_str}'",
                }
            )

        # Validate user exists
        if created_by_user_id_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{created_by_user_id_str}' not found",
                }
            )

        # Check if scene_name already exists in this household (per schema unique constraint)
        for sid, scene in scenes_dict.items():
            if not isinstance(scene, dict):
                continue

            if (
                str(scene.get("home_id")) == household_id_str
                and str(scene.get("scene_name", "")).strip() == scene_name_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Scene with name '{scene_name_str}' already exists in household '{household_id_str}' (scene_id: {sid})",
                    }
                )

        # Generate new scene_id
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_scene_id = generate_id(scenes_dict)

        # Create new scene entry
        new_scene = {
            "scene_id": new_scene_id,
            "home_id": household_id_str,
            "created_by_user_id": created_by_user_id_str,
            "scene_name": scene_name_str,
            "description": description_str,
            "status": status_str,
            "voice_control_phrase": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add to data
        scenes_dict[new_scene_id] = new_scene

        new_scene_return = new_scene.copy()
        new_scene_return["household_id"] = new_scene_return.pop("home_id")

        return json.dumps(
            {
                "success": True,
                "scene": new_scene_return,
                "message": f"Scene '{scene_name_str}' successfully created in household '{home_info.get('home_name')}' with ID: {new_scene_id}",
                "household_name": home_info.get("home_name"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "create_scene",
                "description": (
                    "Create a new scene in a household. "
                    "Validates that the household exists and the user exists. "
                    "Ensures scene_name is unique within the household. "
                    "Status must be 'enabled' or 'disabled'. "
                    "Returns the created scene details including the generated scene_id. "
                    "Note: This only creates the scene record. Use update_scene to add devices and their actions to the scene."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scene_name": {
                            "type": "string",
                            "description": "The name of the scene. Must be unique within the household.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the scene. Accepted values: 'enabled', 'disabled'.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the scene.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household to create the scene in.",
                        },
                        "created_by_user_id": {
                            "type": "string",
                            "description": "The ID of the user creating the scene.",
                        },
                    },
                    "required": [
                        "scene_name",
                        "status",
                        "household_id",
                        "created_by_user_id",
                    ],
                },
            },
        }
