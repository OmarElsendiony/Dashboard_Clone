import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetSceneDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scene_id: str
    ) -> str:
        """
        Get scene details including scene information, scene actions, and scene action attributes.
        """
        # Basic input validation
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

        scene_actions_dict = data.get("scene_actions", {})
        if not isinstance(scene_actions_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid scene_actions container: expected dict at data['scene_actions']"
            })

        scene_action_attributes_dict = data.get("scene_action_attributes", {})
        if not isinstance(scene_action_attributes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid scene_action_attributes container: expected dict at data['scene_action_attributes']"
            })

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid devices container: expected dict at data['devices']"
            })

        # Validate required parameters
        if not scene_id:
            return json.dumps({
                "success": False,
                "error": "scene_id is required"
            })

        scene_id_str = str(scene_id).strip()

        # Find scene by scene_id
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

        # Create scene copy with scene_id
        scene_copy = dict(scene_info)
        scene_copy["scene_id"] = scene_id_str

        # Get all scene actions for this scene
        scene_actions_list = []
        for sa_id, scene_action in scene_actions_dict.items():
            if not isinstance(scene_action, dict):
                continue

            if str(scene_action.get("scene_id")) == scene_id_str:
                action_copy = dict(scene_action)
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
                        attr_copy = dict(attribute)
                        attr_copy["attribute_id"] = str(attr_id)
                        attributes_list.append(attr_copy)

                action_copy["attributes"] = attributes_list
                scene_actions_list.append(action_copy)

        return json.dumps({
            "success": True,
            "scene": scene_copy,
            "scene_actions": scene_actions_list
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_scene_details",
                "description": "Get scene details by scene_id. Returns scene information, all associated scene actions with device information, and all scene action attributes for each action.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scene_id": {
                            "type": "string",
                            "description": "The ID of the scene to retrieve details for."
                        }
                    },
                    "required": ["scene_id"]
                }
            }
        }