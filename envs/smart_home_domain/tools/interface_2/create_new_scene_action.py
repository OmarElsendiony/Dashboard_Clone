import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateNewSceneAction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scene_id: str,
        device_id: str,
        device_attributes: Optional[str] = None
    ) -> str:
        """
        Create a new scene action linking a scene to a device with optional device attributes.
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        scene_actions_dict = data.get("scene_actions", {})
        if not isinstance(scene_actions_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid scene_actions container: expected dict at data['scene_actions']"
            })

        scenes_dict = data.get("scenes", {})
        if not isinstance(scenes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid scenes container: expected dict at data['scenes']"
            })

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid devices container: expected dict at data['devices']"
            })

        scene_action_attributes_dict = data.get("scene_action_attributes", {})
        if not isinstance(scene_action_attributes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid scene_action_attributes container: expected dict at data['scene_action_attributes']"
            })

        # Validate required parameters
        if not scene_id:
            return json.dumps({
                "success": False,
                "error": "scene_id is required"
            })

        if not device_id:
            return json.dumps({
                "success": False,
                "error": "device_id is required"
            })

        scene_id_str = str(scene_id).strip()
        device_id_str = str(device_id).strip()

        # Validate scene exists
        if scene_id_str not in scenes_dict:
            return json.dumps({
                "success": False,
                "error": f"Scene with ID '{scene_id_str}' not found"
            })

        # Validate device exists
        if device_id_str not in devices_dict:
            return json.dumps({
                "success": False,
                "error": f"Device with ID '{device_id_str}' not found"
            })

        # Generate new scene_action_id
        numeric_ids = []
        for key in scene_actions_dict.keys():
            try:
                numeric_ids.append(int(key))
            except (TypeError, ValueError):
                continue
        new_scene_action_id = str(max(numeric_ids, default=0) + 1)

        timestamp = "2025-12-19T23:59:00"

        # Get scene and device info for action_name
        scene_info = scenes_dict[scene_id_str]
        device_info = devices_dict[device_id_str]
        scene_name = scene_info.get("scene_name", "Unknown Scene")
        device_name = device_info.get("device_name", "Unknown Device")

        # Create new scene action record
        new_scene_action = {
            "scene_action_id": new_scene_action_id,
            "scene_id": scene_id_str,
            "device_id": device_id_str,
            "created_at": timestamp,
            "action_name": f"{scene_name} - Control {device_name}"
        }

        # Add to data
        scene_actions_dict[new_scene_action_id] = new_scene_action

        # Parse and create device attributes if provided
        created_attributes = []
        if device_attributes:
            try:
                # Try to parse as JSON string
                if isinstance(device_attributes, str):
                    attrs_dict = json.loads(device_attributes)
                else:
                    attrs_dict = device_attributes

                if not isinstance(attrs_dict, dict):
                    return json.dumps({
                        "success": False,
                        "error": "device_attributes must be a dictionary or JSON string representing a dictionary"
                    })

                # Generate attribute IDs
                attr_numeric_ids = []
                for key in scene_action_attributes_dict.keys():
                    try:
                        attr_numeric_ids.append(int(key))
                    except (TypeError, ValueError):
                        continue

                # Create attribute records
                for attr_name, attr_value in attrs_dict.items():
                    if not isinstance(attr_name, str) or not attr_name.strip():
                        continue

                    new_attr_id = str(max(attr_numeric_ids, default=0) + 1)
                    attr_numeric_ids.append(int(new_attr_id))

                    attr_value_str = str(attr_value) if attr_value is not None else ""

                    new_attribute = {
                        "attribute_id": new_attr_id,
                        "scene_action_id": new_scene_action_id,
                        "attribute_name": attr_name.strip(),
                        "attribute_value": attr_value_str,
                        "created_at": timestamp,
                        "attribute_description": f"Configure {attr_name.strip()}: {attr_value_str}"
                    }

                    scene_action_attributes_dict[new_attr_id] = new_attribute
                    created_attributes.append(new_attribute)

            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "device_attributes must be a valid JSON string"
                })
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": f"Error processing device_attributes: {str(e)}"
                })

        return json.dumps({
            "success": True,
            "scene_action": new_scene_action,
            "attributes": created_attributes
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_scene_action",
                "description": "Create a new scene action linking a scene to a device. Optionally accepts device_attributes as a JSON string or dictionary to create scene action attributes. Validates that the scene and device exist before creating the action.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scene_id": {
                            "type": "string",
                            "description": "The ID of the scene to add the action to."
                        },
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to control in this scene action."
                        },
                        "device_attributes": {
                            "type": "string",
                            "description": "Optional JSON string representing a dictionary of device attributes (e.g., {\"power\": \"on\", \"brightness\": 75})."
                        }
                    },
                    "required": ["scene_id", "device_id"]
                }
            }
        }