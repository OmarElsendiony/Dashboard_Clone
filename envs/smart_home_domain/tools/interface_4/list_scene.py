import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class ListScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        household_id: str,
        scene_name: str,
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

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid homes container: expected dict at data['homes']",
                }
            )

        scene_actions_dict = data.get("scene_actions", {})
        if not isinstance(scene_actions_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid scene_actions container: expected dict at data['scene_actions']",
                }
            )

        scene_action_attributes_dict = data.get("scene_action_attributes", {})
        if not isinstance(scene_action_attributes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid scene_action_attributes container: expected dict at data['scene_action_attributes']",
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

        # Validate required parameters
        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        if not scene_name:
            return json.dumps({"success": False, "error": "scene_name is required"})

        # Convert to strings for consistent comparison
        household_id_str = str(household_id).strip()
        scene_name_str = str(scene_name).strip()

        # Check if household exists
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

        # Find scene by name in the specified household
        scene_id = None
        scene_info = None
        for sid, scene in scenes_dict.items():
            if not isinstance(scene, dict):
                continue

            if (
                str(scene.get("home_id")) == household_id_str
                and str(scene.get("scene_name", "")).strip() == scene_name_str
            ):
                scene_id = str(sid)
                scene_info = scene.copy()
                scene_info["scene_id"] = scene_id
                break

        if scene_info is None:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Scene with name '{scene_name_str}' not found in household '{household_id_str}'",
                }
            )

        # Get all scene actions for this scene
        scene_actions_list = []
        for sa_id, scene_action in scene_actions_dict.items():
            if not isinstance(scene_action, dict):
                continue

            if str(scene_action.get("scene_id")) == scene_id:
                action_copy = scene_action.copy()
                action_copy["scene_action_id"] = str(sa_id)

                # Get device information
                device_id = str(action_copy.get("device_id"))
                if device_id in devices_dict:
                    device = devices_dict[device_id]
                    if isinstance(device, dict):
                        action_copy["device_name"] = device.get("device_name")
                        action_copy["device_type"] = device.get("device_type")

                # Get all attributes for this scene action
                attributes_list = []
                for attr_id, attribute in scene_action_attributes_dict.items():
                    if not isinstance(attribute, dict):
                        continue

                    if str(attribute.get("scene_action_id")) == str(sa_id):
                        attr_copy = attribute.copy()
                        attr_copy["attribute_id"] = str(attr_id)
                        attributes_list.append(attr_copy)

                action_copy["attributes"] = attributes_list
                scene_actions_list.append(action_copy)

        return json.dumps(
            {
                "success": True,
                "scene": scene_info,
                "scene_actions": scene_actions_list,
                "message": f"Scene '{scene_name_str}' found successfully in household '{home_info.get('home_name')}'",
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
                "name": "list_scene",
                "description": (
                    "Retrieve scene information by scene name and household ID. "
                    "Returns scene details including scene_id, scene_name, description, "
                    "status (enabled/disabled), voice_control_phrase, created_by_user_id, and timestamps. "
                    "Also returns all scene actions associated with the scene, including device information "
                    "and attributes (such as power, brightness, color, temperature settings). "
                    "Validates that the household exists. "
                    "Returns an error if the household doesn't exist or the scene is not found in the specified household."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household where the scene is located.",
                        },
                        "scene_name": {
                            "type": "string",
                            "description": "The name of the scene to retrieve.",
                        },
                    },
                    "required": ["household_id", "scene_name"],
                },
            },
        }
