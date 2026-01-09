import json
from typing import Any, Dict, Optional, List, Union
from tau_bench.envs.tool import Tool


class AddRoutineAction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action_type: str,
        routine_id: str,
        action_parameters: Optional[Dict[str, Any]] = None,
        action_attributes: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        # 1. Routine Validation
        routines = data.get("routines", {})
        routine = routines.get(routine_id)
        if not routine:
            return json.dumps({"success": False, "error": "Routine not found"})

        # 2. Action Type Validation
        valid_action_types = ["device_control", "scene_activation", "notification"]
        if action_type not in valid_action_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action type. Must be one of {valid_action_types}",
                }
            )

        # 3. Extract action parameters
        target_device_id = (
            action_parameters.get("target_device_id") if action_parameters else None
        )
        target_scene_id = (
            action_parameters.get("target_scene_id") if action_parameters else None
        )
        target_notification_id = (
            action_parameters.get("target_notification_id")
            if action_parameters
            else None
        )

        # 4. Validate based on action type
        attribute_list = []

        if action_type == "device_control":
            if not target_device_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "target_device_id is required for device_control actions",
                    }
                )

            devices = data.get("devices", {})
            device = devices.get(target_device_id)
            if not device:
                return json.dumps({"success": False, "error": "Device not found"})

            device_type = device.get("device_type")

            # Define validation rules based on device type
            validation_rules = {
                "camera": {
                    "power": ["on", "off"],
                    "recording": ["recording", "paused", "stopped"],
                    "motion_detection": ["motion_detected", "clear"],
                },
                "bulb": {"power": ["on", "off"], "brightness": (0, 100)},
                "thermostat": {
                    "power": ["on", "off"],
                    "mode": ["heating", "cooling", "idle"],
                    "temperature": (32, 104),
                    "target_temperature": (60, 90),
                },
                "speaker": {
                    "power": ["on", "off"],
                    "playback_state": ["playing", "paused", "stopped"],
                    "volume": (0, 100),
                    "mute": ["muted", "unmuted"],
                },
                "door_lock": {"lock_state": ["locked", "unlocked"]},
                "motion_sensor": {"motion_state": ["motion_detected", "clear"]},
                "temperature_sensor": {"temperature": (32, 104)},
                "humidity_sensor": {"humidity": (0, 100)},
                "light_sensor": {"brightness_level": (0, 65535)},
                "door_sensor": {"door_state": ["open", "closed"]},
                "water_leak_sensor": {"leak_state": ["leak_detected", "no_leak"]},
                "smoke_detector_sensor": {
                    "smoke_state": ["smoke_detected", "no_smoke", "alarm_triggered"]
                },
                "power_outlet": {
                    "power": ["on", "off"],
                    "power_consumption": (0, 3680),
                },
                "air_conditioner": {
                    "power": ["on", "off"],
                    "mode": ["cooling", "idle"],
                    "temperature": (32, 104),
                    "target_temperature": (60, 85),
                },
            }

            rules = validation_rules.get(device_type)
            if not rules:
                return json.dumps(
                    {"success": False, "error": f"Unknown device type '{device_type}'"}
                )

            # Process action attributes
            if action_attributes:
                # Normalize to list
                if isinstance(action_attributes, dict):
                    attrs_to_process = [action_attributes]
                elif isinstance(action_attributes, list):
                    attrs_to_process = action_attributes
                else:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "action_attributes must be a dict or list of dicts",
                        }
                    )

                # Process each attribute dict
                for attr_dict in attrs_to_process:
                    if not isinstance(attr_dict, dict):
                        return json.dumps(
                            {
                                "success": False,
                                "error": "Each item in action_attributes must be a dict",
                            }
                        )

                    # Process all attributes in this dict
                    for attr_name, attr_val in attr_dict.items():
                        # Validate attribute
                        if attr_name not in rules:
                            return json.dumps(
                                {
                                    "success": False,
                                    "error": f"Invalid attribute '{attr_name}' for device type '{device_type}'",
                                }
                            )

                        allowed = rules[attr_name]
                        # Validate numeric ranges
                        if isinstance(allowed, tuple):
                            try:
                                val_float = float(attr_val)
                                if not (allowed[0] <= val_float <= allowed[1]):
                                    return json.dumps(
                                        {
                                            "success": False,
                                            "error": f"Value {attr_val} out of range for {attr_name} ({allowed[0]}-{allowed[1]})",
                                        }
                                    )
                            except (ValueError, TypeError):
                                return json.dumps(
                                    {
                                        "success": False,
                                        "error": f"Value {attr_val} must be a number for {attr_name}",
                                    }
                                )
                        # Validate categorical strings
                        elif isinstance(allowed, list):
                            if attr_val not in allowed:
                                return json.dumps(
                                    {
                                        "success": False,
                                        "error": f"Invalid value '{attr_val}' for {attr_name}. Expected one of {allowed}",
                                    }
                                )

                        # Store validated attribute
                        attribute_list.append(
                            {"attribute_name": attr_name, "attribute_value": attr_val}
                        )
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": "action_attributes required for device_control actions",
                    }
                )

        elif action_type == "scene_activation":
            if not target_scene_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "target_scene_id is required for scene_activation actions",
                    }
                )

            scenes = data.get("scenes", {})
            if target_scene_id not in scenes:
                return json.dumps({"success": False, "error": "Scene not found"})

        elif action_type == "notification":
            if not target_notification_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "target_notification_id is required for notification actions",
                    }
                )

            notifications = data.get("notifications", {})
            if target_notification_id not in notifications:
                return json.dumps({"success": False, "error": "Notification not found"})

        # 5. Data Persistence
        routine_actions = data.get("routine_actions", {})
        next_action_id = str(generate_id(routine_actions))
        timestamp = "2025-12-19T23:59:00"

        action = {
            "action_id": next_action_id,
            "routine_id": routine_id,
            "action_type": action_type,
            "target_device_id": target_device_id,
            "target_scene_id": target_scene_id,
            "target_notification_id": target_notification_id,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        routine_actions[next_action_id] = action
        data["routine_actions"] = routine_actions

        # Save all attributes
        saved_attributes = []
        if attribute_list:
            routine_action_attributes = data.get("routine_action_attributes", {})
            for attr_info in attribute_list:
                next_attr_id = str(generate_id(routine_action_attributes))
                routine_action_attribute = {
                    "attribute_id": next_attr_id,
                    "action_id": next_action_id,
                    "attribute_name": attr_info["attribute_name"],
                    "attribute_value": attr_info["attribute_value"],
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                routine_action_attributes[next_attr_id] = routine_action_attribute
                saved_attributes.append(routine_action_attribute)
            data["routine_action_attributes"] = routine_action_attributes

        return json.dumps(
            {
                "success": True,
                "routine_action": action,
                "attributes": saved_attributes if saved_attributes else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_routine_action",
                "description": "Add an action to a specified routine in a smart home system. Supports three action types: device_control (control device states), scene_activation (activate predefined scenes), and notification (send alerts). For device_control actions, attributes are validated based on device type. Pass attributes directly as key-value pairs in action_attributes dict(s). Multiple attributes can be specified in a single dict {'power': 'on', 'brightness': 75} or as a list of dicts. Device attributes by type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {
                            "type": "string",
                            "enum": [
                                "device_control",
                                "scene_activation",
                                "notification",
                            ],
                            "description": "The type of action: 'device_control' (control device states with attributes), 'scene_activation' (activate a predefined scene), or 'notification' (send an alert to users).",
                        },
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to which the action will be added.",
                        },
                        "action_parameters": {
                            "type": "object",
                            "description": "Parameters for the action based on action_type. For device_control: requires 'target_device_id'. For scene_activation: requires 'target_scene_id'. For notification: requires 'target_notification_id'.",
                            "properties": {
                                "target_device_id": {
                                    "type": "string",
                                    "description": "The ID of the device to control (required for device_control actions). Must reference a valid device_id from the devices table.",
                                },
                                "target_scene_id": {
                                    "type": "string",
                                    "description": "The ID of the scene to activate (required for scene_activation actions). Must reference a valid scene_id from the scenes table.",
                                },
                                "target_notification_id": {
                                    "type": "string",
                                    "description": "The ID of the pre-configured notification to send (required for notification actions). Must reference a valid notification_id from the notifications table.",
                                },
                            },
                        },
                        "action_attributes": {
                            "type": "array",
                            "description": "For device_control actions: either a single dict or list of dicts containing device attributes to set. Each dict can contain multiple attributes as direct key-value pairs. Examples: {'power': 'on', 'brightness': 75} or [{'power': 'on'}, {'temperature': 72}]. Required for device_control, not used for other action types.",
                            "properties": {
                                "power": {
                                    "type": "string",
                                    "description": "Power state: 'on' or 'off'",
                                },
                                "brightness": {
                                    "type": "number",
                                    "description": "Brightness level (0-100)",
                                },
                                "recording": {
                                    "type": "string",
                                    "description": "Recording state: 'recording', 'paused', or 'stopped'",
                                },
                                "motion_detection": {
                                    "type": "string",
                                    "description": "Motion detection state: 'motion_detected' or 'clear'",
                                },
                                "mode": {
                                    "type": "string",
                                    "description": "Device mode (varies by device type)",
                                },
                                "temperature": {
                                    "type": "number",
                                    "description": "Current temperature (32-104°F)",
                                },
                                "target_temperature": {
                                    "type": "number",
                                    "description": "Target temperature (60-90°F for thermostat, 60-85°F for AC)",
                                },
                                "playback_state": {
                                    "type": "string",
                                    "description": "Playback state: 'playing', 'paused', or 'stopped'",
                                },
                                "volume": {
                                    "type": "number",
                                    "description": "Volume level (0-100)",
                                },
                                "mute": {
                                    "type": "string",
                                    "description": "Mute state: 'muted' or 'unmuted'",
                                },
                                "lock_state": {
                                    "type": "string",
                                    "description": "Lock state: 'locked' or 'unlocked'",
                                },
                                "motion_state": {
                                    "type": "string",
                                    "description": "Motion state: 'motion_detected' or 'clear'",
                                },
                                "humidity": {
                                    "type": "number",
                                    "description": "Humidity level (0-100%)",
                                },
                                "brightness_level": {
                                    "type": "number",
                                    "description": "Light sensor brightness (0-65535 lux)",
                                },
                                "door_state": {
                                    "type": "string",
                                    "description": "Door state: 'open' or 'closed'",
                                },
                                "leak_state": {
                                    "type": "string",
                                    "description": "Leak state: 'leak_detected' or 'no_leak'",
                                },
                                "smoke_state": {
                                    "type": "string",
                                    "description": "Smoke state: 'smoke_detected', 'no_smoke', or 'alarm_triggered'",
                                },
                                "power_consumption": {
                                    "type": "number",
                                    "description": "Power consumption (0-3680 watts)",
                                },
                            },
                        },
                    },
                    "required": ["action_type", "routine_id"],
                },
            },
        }
