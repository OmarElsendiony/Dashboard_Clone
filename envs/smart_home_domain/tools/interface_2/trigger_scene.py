import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class TriggerScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scene_id: str
    ) -> str:
        """
        Trigger a scene by applying all scene actions to their respective devices, creating device states and device state attributes.
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

        device_states_dict = data.get("device_states", {})
        if not isinstance(device_states_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid device_states container: expected dict at data['device_states']"
            })

        device_state_attributes_dict = data.get("device_state_attributes", {})
        if not isinstance(device_state_attributes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid device_state_attributes container: expected dict at data['device_state_attributes']"
            })

        # Validate required parameters
        if not scene_id:
            return json.dumps({
                "success": False,
                "error": "scene_id is required"
            })

        scene_id_str = str(scene_id).strip()

        # Validate scene exists
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

        # Check if scene is enabled
        if scene_info.get("status") != "enabled":
            return json.dumps({
                "success": False,
                "error": f"Scene with ID '{scene_id_str}' is not enabled"
            })

        # Get all scene actions for this scene
        scene_actions_for_scene = []
        for sa_id, scene_action in scene_actions_dict.items():
            if not isinstance(scene_action, dict):
                continue
            if str(scene_action.get("scene_id")) == scene_id_str:
                scene_actions_for_scene.append((sa_id, scene_action))

        if not scene_actions_for_scene:
            return json.dumps({
                "success": False,
                "error": f"No scene actions found for scene '{scene_id_str}'"
            })

        timestamp = "2025-12-19T23:59:00"
        triggered_devices = []

        # Generate IDs for device_states
        state_numeric_ids = []
        for key in device_states_dict.keys():
            try:
                state_numeric_ids.append(int(key))
            except (TypeError, ValueError):
                continue

        # Generate IDs for device_state_attributes
        attr_numeric_ids = []
        for key in device_state_attributes_dict.keys():
            try:
                attr_numeric_ids.append(int(key))
            except (TypeError, ValueError):
                continue

        # Process each scene action
        for sa_id, scene_action in scene_actions_for_scene:
            device_id = str(scene_action.get("device_id"))

            # Validate device exists
            if device_id not in devices_dict:
                continue

            device_info = devices_dict[device_id]
            if not isinstance(device_info, dict):
                continue

            device_name = device_info.get("device_name", "Unknown Device")

            # Create new device_state
            new_state_id = str(max(state_numeric_ids, default=0) + 1)
            state_numeric_ids.append(int(new_state_id))

            new_device_state = {
                "state_id": new_state_id,
                "device_id": device_id,
                "changed_at": timestamp,
                "created_at": timestamp,
                "state_summary": f"{device_name} state changed on {timestamp}"
            }

            device_states_dict[new_state_id] = new_device_state

            # Get all attributes for this scene action
            scene_attributes = []
            for attr_id, attribute in scene_action_attributes_dict.items():
                if not isinstance(attribute, dict):
                    continue
                if str(attribute.get("scene_action_id")) == str(sa_id):
                    scene_attributes.append(attribute)

            # Create device_state_attributes for each scene_action_attribute
            created_attributes = []
            for scene_attr in scene_attributes:
                new_attr_id = str(max(attr_numeric_ids, default=0) + 1)
                attr_numeric_ids.append(int(new_attr_id))

                attr_name = scene_attr.get("attribute_name", "")
                attr_value = scene_attr.get("attribute_value", "")

                new_device_state_attribute = {
                    "attribute_id": new_attr_id,
                    "state_id": new_state_id,
                    "attribute_name": attr_name,
                    "attribute_value": str(attr_value),
                    "created_at": timestamp,
                    "state_description": f"Device state value: "
                }

                device_state_attributes_dict[new_attr_id] = new_device_state_attribute
                created_attributes.append(new_device_state_attribute)

            triggered_devices.append({
                "device_id": device_id,
                "device_name": device_name,
                "state_id": new_state_id,
                "attributes": created_attributes
            })

        return json.dumps({
            "success": True,
            "scene_id": scene_id_str,
            "scene_name": scene_info.get("scene_name"),
            "triggered_devices": triggered_devices,
            "message": f"Scene '{scene_info.get('scene_name')}' triggered successfully"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "trigger_scene",
                "description": "Trigger a scene by applying all scene actions to their respective devices. Creates device states and device state attributes for each device in the scene. Validates that the scene exists and is enabled before triggering.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scene_id": {
                            "type": "string",
                            "description": "The ID of the scene to trigger."
                        }
                    },
                    "required": ["scene_id"]
                }
            }
        }
