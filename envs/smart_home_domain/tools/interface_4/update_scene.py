import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class UpdateScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scene_id: str,
        scene_status: Optional[str] = None,
        scene_name: Optional[str] = None,
        description: Optional[str] = None,
        device_id: Optional[str] = None,
        device_attribute_value_list: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

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
        if not scene_id:
            return json.dumps({"success": False, "error": "scene_id is required"})

        # Check that at least one update parameter is provided
        if not scene_status and not scene_name and not description and not device_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one of scene_status, scene_name, description, or device_id must be provided for update",
                }
            )

        # Convert to strings for consistent comparison
        scene_id_str = str(scene_id).strip()
        scene_status_str = str(scene_status).strip() if scene_status else None
        scene_name_str = str(scene_name).strip() if scene_name else None
        description_str = str(description).strip() if description else None
        device_id_str = str(device_id).strip() if device_id else None

        # Validate scene_status if provided
        if scene_status_str:
            valid_statuses = ["enabled", "disabled"]
            if scene_status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid scene_status '{scene_status_str}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )

        # Check if scene exists
        if scene_id_str not in scenes_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Scene with ID '{scene_id_str}' not found",
                }
            )

        scene = scenes_dict[scene_id_str]
        if not isinstance(scene, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid scene data for ID '{scene_id_str}'",
                }
            )

        household_id_str = str(scene.get("home_id"))

        # Track updates made
        updates_made = []
        new_scene_action = None
        created_attributes = []

        # Check if new scene_name conflicts with existing scenes (excluding current scene)
        if scene_name_str is not None:
            for sid, sc in scenes_dict.items():
                if not isinstance(sc, dict):
                    continue

                # Skip the current scene being updated
                if str(sid) == scene_id_str:
                    continue

                if (
                    str(sc.get("home_id")) == household_id_str
                    and str(sc.get("scene_name", "")).strip() == scene_name_str
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Scene with name '{scene_name_str}' already exists in household '{household_id_str}' (scene_id: {sid})",
                        }
                    )

            # Update scene name
            old_scene_name = scene.get("scene_name")
            scene["scene_name"] = scene_name_str
            updates_made.append(
                f"scene_name from '{old_scene_name}' to '{scene_name_str}'"
            )

        # Update description if provided
        if description_str:
            scene["description"] = description_str
            updates_made.append(f"description to '{description_str}'")

        # Update scene status if provided
        if scene_status_str:
            scene["status"] = scene_status_str
            updates_made.append(f"status to '{scene_status_str}'")

        # Handle device addition if device_id is provided
        if device_id_str:
            # Validate device_attribute_value_list
            if not device_attribute_value_list:
                return json.dumps(
                    {
                        "success": False,
                        "error": "device_attribute_value_list is required when device_id is provided",
                    }
                )

            if not isinstance(device_attribute_value_list, list):
                return json.dumps(
                    {
                        "success": False,
                        "error": "device_attribute_value_list must be a list",
                    }
                )

            if len(device_attribute_value_list) == 0:
                return json.dumps(
                    {
                        "success": False,
                        "error": "device_attribute_value_list cannot be empty when device_id is provided. At least one attribute must be specified.",
                    }
                )

            for attr in device_attribute_value_list:
                if not isinstance(attr, dict):
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Each item in device_attribute_value_list must be a dict with 'attribute_name' and 'attribute_value'",
                        }
                    )
                if "attribute_name" not in attr or "attribute_value" not in attr:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Each attribute must have 'attribute_name' and 'attribute_value' keys",
                        }
                    )

            # Check if device exists
            if device_id_str not in devices_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device with ID '{device_id_str}' not found",
                    }
                )

            device = devices_dict[device_id_str]
            if not isinstance(device, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid device data for ID '{device_id_str}'",
                    }
                )

            # Verify device belongs to the same household as the scene
            if str(device.get("home_id")) != household_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device '{device_id_str}' does not belong to the same household as scene '{scene_id_str}'",
                    }
                )

            # Generate new IDs
            def generate_id(table: Dict[str, Any]) -> str:
                """Generates a new unique ID for a record."""
                if not table:
                    return "1"
                return str(max(int(k) for k in table.keys()) + 1)

            # Create scene_action entry
            new_scene_action_id = generate_id(scene_actions_dict)
            new_scene_action = {
                "scene_action_id": new_scene_action_id,
                "scene_id": scene_id_str,
                "device_id": device_id_str,
                "created_at": timestamp,
            }
            scene_actions_dict[new_scene_action_id] = new_scene_action

            # Create scene_action_attributes entries
            for attr in device_attribute_value_list:
                attribute_name = str(attr["attribute_name"]).strip()
                attribute_value = str(attr["attribute_value"]).strip()

                new_attribute_id = generate_id(scene_action_attributes_dict)
                new_attribute = {
                    "attribute_id": new_attribute_id,
                    "scene_action_id": new_scene_action_id,
                    "attribute_name": attribute_name,
                    "attribute_value": attribute_value,
                    "created_at": timestamp,
                }
                scene_action_attributes_dict[new_attribute_id] = new_attribute
                created_attributes.append(new_attribute)

            updates_made.append(
                f"added device '{device.get('device_name')}' with {len(created_attributes)} attribute(s)"
            )

        # Update timestamp
        scene["updated_at"] = timestamp

        scene_return = scene.copy()
        scene_return["household_id"] = scene_return.pop("home_id")

        result = {
            "success": True,
            "scene": scene_return,
            "message": f"Scene '{scene.get('scene_name')}' updated successfully.",
        }

        if new_scene_action is not None:
            result["scene_action"] = new_scene_action
            result["scene_action_attributes"] = created_attributes

        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_scene",
                "description": (
                    "Update a scene by modifying its name, description, status, and/or adding devices with their actions and attributes. "
                    "At least one of scene_status, scene_name, description, or device_id must be provided. "
                    "If scene_name is provided, ensures it's unique within the household (excluding the current scene). "
                    "If scene_status is provided, must be 'enabled' or 'disabled'. "
                    "If device_id is provided, device_attribute_value_list is required and must be a list of dicts, "
                    "each containing 'attribute_name' and 'attribute_value'. "
                    "Example: [{'attribute_name': 'power', 'attribute_value': 'on'}, {'attribute_name': 'brightness', 'attribute_value': '75'}]. "
                    "Creates scene_actions and scene_action_attributes entries for the specified device when device_id is provided. "
                    "Validates that the scene exists, and if adding a device, that the device exists and belongs to the same household. "
                    "This function can be called multiple times to add multiple devices to the scene or to update scene metadata."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scene_id": {
                            "type": "string",
                            "description": "The ID of the scene to update.",
                        },
                        "scene_status": {
                            "type": "string",
                            "description": "Optional. The status to set for the scene. Accepted values: 'enabled', 'disabled'.",
                        },
                        "scene_name": {
                            "type": "string",
                            "description": "Optional. The new name for the scene. Must be unique within the household.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. The new description for the scene.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Optional. The ID of the device to add to the scene. If provided, device_attribute_value_list is required.",
                        },
                        "device_attribute_value_list": {
                            "type": "array",
                            "description": (
                                "Optional. Required when device_id is provided. List of attribute dictionaries, each with 'attribute_name' and 'attribute_value' keys. "
                                "Accepted attributes by device type: "
                                "camera: power (on/off), recording (recording/paused/stopped), motion_detection (motion_detected/clear); "
                                "bulb: power (on/off), brightness (0-100), color (hex code or color name); "
                                "thermostat: power (on/off), mode (heating/cooling/idle), temperature (32-104), target_temperature (60-90); "
                                "speaker: power (on/off), playback_state (playing/paused/stopped), volume (0-100), mute (muted/unmuted); "
                                "door_lock: lock_state (locked/unlocked); "
                                "motion_sensor: motion_state (motion_detected/clear); "
                                "temperature_sensor: temperature (32-104); "
                                "humidity_sensor: humidity (0-100); "
                                "light_sensor: brightness_level (0-65535); "
                                "door_sensor: door_state (open/closed); "
                                "water_leak_sensor: leak_state (leak_detected/no_leak); "
                                "smoke_detector_sensor: smoke_state (smoke_detected/no_smoke/alarm_triggered); "
                                "power_outlet: power (on/off), power_consumption (0-3680); "
                                "air_conditioner: power (on/off), mode (cooling/idle), temperature (32-104), target_temperature (60-85). "
                                "Example: [{'attribute_name': 'power', 'attribute_value': 'on'}, {'attribute_name': 'brightness', 'attribute_value': '75'}]"
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "attribute_name": {
                                        "type": "string",
                                        "description": "The name of the attribute (e.g., 'power', 'brightness', 'color', 'temperature')",
                                    },
                                    "attribute_value": {
                                        "type": "string",
                                        "description": "The value for the attribute (e.g., 'on', '75', '#FF5733', '72')",
                                    },
                                },
                            },
                        },
                    },
                    "required": ["scene_id"],
                },
            },
        }
