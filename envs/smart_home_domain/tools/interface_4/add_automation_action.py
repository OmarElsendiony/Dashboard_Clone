import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class AddAutomationAction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        automation_id: str,
        action_type: str,
        device_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        attribute_name: Optional[str] = None,
        attribute_value: Optional[str] = None,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        routines_dict = data.get("routines", {})
        if not isinstance(routines_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routines container: expected dict at data['routines']",
                }
            )

        routine_actions_dict = data.get("routine_actions", {})
        if not isinstance(routine_actions_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routine_actions container: expected dict at data['routine_actions']",
                }
            )

        routine_action_attributes_dict = data.get("routine_action_attributes", {})
        if not isinstance(routine_action_attributes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routine_action_attributes container: expected dict at data['routine_action_attributes']",
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

        scenes_dict = data.get("scenes", {})
        if not isinstance(scenes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid scenes container: expected dict at data['scenes']",
                }
            )

        notifications_dict = data.get("notifications", {})
        if not isinstance(notifications_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid notifications container: expected dict at data['notifications']",
                }
            )

        # Validate required parameters
        if not automation_id:
            return json.dumps({"success": False, "error": "automation_id is required"})

        if not action_type:
            return json.dumps({"success": False, "error": "action_type is required"})

        # Convert to strings for consistent comparison
        automation_id_str = str(automation_id).strip()
        action_type_str = str(action_type).strip()
        device_id_str = str(device_id).strip() if device_id else None
        scene_id_str = str(scene_id).strip() if scene_id else None
        notification_id_str = str(notification_id).strip() if notification_id else None
        attribute_name_str = str(attribute_name).strip() if attribute_name else None
        attribute_value_str = str(attribute_value).strip() if attribute_value else None

        # Validate action_type
        valid_action_types = ["device_control", "scene_activation", "notification"]
        if action_type_str not in valid_action_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action_type '{action_type_str}'. Must be one of: {', '.join(valid_action_types)}",
                }
            )

        # Check if automation exists
        if automation_id_str not in routines_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Automation with ID '{automation_id_str}' not found",
                }
            )

        automation = routines_dict[automation_id_str]
        if not isinstance(automation, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid automation data for ID '{automation_id_str}'",
                }
            )

        household_id_str = str(automation.get("home_id"))

        # Validate based on action_type
        if action_type_str == "device_control":
            if not device_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "device_id is required for action_type 'device_control'",
                    }
                )

            if not attribute_name_str or not attribute_value_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "attribute_name and attribute_value are required for action_type 'device_control'",
                    }
                )

            # Validate device exists
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

            # Verify device belongs to the same household
            if str(device.get("home_id")) != household_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device '{device_id_str}' does not belong to the same household as automation '{automation_id_str}'",
                    }
                )

        elif action_type_str == "scene_activation":
            if not scene_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "scene_id is required for action_type 'scene_activation'",
                    }
                )

            # Validate scene exists
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

            # Verify scene belongs to the same household
            if str(scene.get("home_id")) != household_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Scene '{scene_id_str}' does not belong to the same household as automation '{automation_id_str}'",
                    }
                )

        elif action_type_str == "notification":
            if not notification_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "notification_id is required for action_type 'notification'",
                    }
                )

            # Validate notification exists
            if notification_id_str not in notifications_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Notification with ID '{notification_id_str}' not found",
                    }
                )

            notification = notifications_dict[notification_id_str]
            if not isinstance(notification, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid notification data for ID '{notification_id_str}'",
                    }
                )

        # Generate new IDs
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        # Create routine_action entry
        new_action_id = generate_id(routine_actions_dict)
        new_action = {
            "action_id": new_action_id,
            "routine_id": automation_id_str,
            "action_type": action_type_str,
            "target_device_id": device_id_str,
            "target_scene_id": scene_id_str,
            "target_notification_id": notification_id_str,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routine_actions_dict[new_action_id] = new_action

        new_action_return = new_action.copy()
        new_action_return["automation_id"] = new_action_return.pop("routine_id")

        # Create routine_action_attributes if device_control
        created_attributes = []
        if action_type_str == "device_control":
            new_attribute_id = generate_id(routine_action_attributes_dict)
            new_attribute = {
                "attribute_id": new_attribute_id,
                "action_id": new_action_id,
                "attribute_name": attribute_name_str,
                "attribute_value": attribute_value_str,
                "created_at": timestamp,
            }
            routine_action_attributes_dict[new_attribute_id] = new_attribute
            created_attributes.append(new_attribute)

        result = {
            "success": True,
            "action": new_action,
            "message": f"Action successfully added to automation '{automation.get('routine_name')}' with ID: {new_action_id}",
        }

        if created_attributes:
            result["attributes"] = created_attributes

        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_automation_action",
                "description": (
                    "Add an action to an automation. "
                    "Validates that the automation exists. "
                    "action_type must be one of: device_control, scene_activation, notification. "
                    "For 'device_control': device_id, attribute_name, and attribute_value are required. "
                    "Validates device exists and belongs to the same household. Creates routine_action_attributes entry. "
                    "For 'scene_activation': scene_id is required. Validates scene exists and belongs to the same household. "
                    "For 'notification': notification_id is required. Validates notification exists. "
                    "Device attributes are validated based on device type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85)."
                    "Returns the created action details and attributes (if applicable)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "automation_id": {
                            "type": "string",
                            "description": "The ID of the automation to add the action to.",
                        },
                        "action_type": {
                            "type": "string",
                            "description": "The type of action. Accepted values: 'device_control', 'scene_activation', 'notification'.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Required for action_type 'device_control'. The ID of the device to control.",
                        },
                        "scene_id": {
                            "type": "string",
                            "description": "Required for action_type 'scene_activation'. The ID of the scene to activate.",
                        },
                        "notification_id": {
                            "type": "string",
                            "description": "Required for action_type 'notification'. The ID of the notification to send.",
                        },
                        "attribute_name": {
                            "type": "string",
                            "description": "Required for action_type 'device_control'. The name of the device attribute to control (e.g., 'power', 'brightness', 'temperature').",
                        },
                        "attribute_value": {
                            "type": "string",
                            "description": "Required for action_type 'device_control'. The value to set for the device attribute (e.g., 'on', '75', '72').",
                        },
                    },
                    "required": ["automation_id", "action_type"],
                },
            },
        }
