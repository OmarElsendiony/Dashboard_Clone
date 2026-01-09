import json
from typing import Any, Dict, Optional, List, Union
from tau_bench.envs.tool import Tool


class UpdateRoutineAction(Tool):
    """
    Update a routine action and its attributes with comprehensive validation.
    - Requires routine_id, action_id, and updates dict.
    - Can update action properties (action_type, target_device_id, etc.)
    - Can update device control attributes via action_attributes parameter
    - Validates that routine and action exist.
    - For device_control actions, validates device type and attributes.
    - Updates the 'updated_at' timestamp automatically.
    - Cannot update action_id, routine_id, or created_at.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        routine_id: str,
        action_id: str,
        updates: Dict[str, Any],
        action_attributes: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ) -> str:
        """
        Update a routine action and optionally its attributes.

        Args:
            data: The data dictionary containing routines and routine_actions
            routine_id: The ID of the routine
            action_id: The ID of the action to update
            updates: Dictionary of action fields to update
            action_attributes: Optional dict or list of dicts with attributes to update/add

        Returns:
            JSON string with success status and updated action information
        """
        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

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

        # Validate required fields
        if routine_id is None:
            return json.dumps({"success": False, "error": "routine_id is required"})

        if action_id is None:
            return json.dumps({"success": False, "error": "action_id is required"})

        if not isinstance(updates, dict):
            return json.dumps(
                {"success": False, "error": "updates must be a dictionary"}
            )

        if not updates and not action_attributes:
            return json.dumps(
                {
                    "success": False,
                    "error": "Either updates or action_attributes must be provided",
                }
            )

        # Convert to strings for consistent comparison
        routine_id_str = str(routine_id)
        action_id_str = str(action_id)

        # Validate routine exists
        if routine_id_str not in routines_dict:
            return json.dumps(
                {"success": False, "error": f"Routine not found: '{routine_id_str}'"}
            )

        # Validate action exists
        if action_id_str not in routine_actions_dict:
            return json.dumps(
                {"success": False, "error": f"Action not found: '{action_id_str}'"}
            )

        action_data = routine_actions_dict[action_id_str]

        # Validate action belongs to the specified routine
        if str(action_data.get("routine_id")) != routine_id_str:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Action '{action_id_str}' does not belong to routine '{routine_id_str}'",
                }
            )

        # Validate that protected fields are not in updates
        protected_fields = ["action_id", "routine_id", "created_at"]
        for field in protected_fields:
            if field in updates:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot update protected field: '{field}'",
                    }
                )

        # Valid action types
        valid_action_types = ["device_control", "scene_activation", "notification"]

        # Validate updates values
        for key, value in updates.items():
            if key == "action_type":
                if value not in valid_action_types:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid action_type: '{value}'. Must be one of {valid_action_types}",
                        }
                    )

            elif key == "target_device_id":
                if value is not None and str(value) not in devices_dict:
                    return json.dumps(
                        {"success": False, "error": f"Device not found: '{value}'"}
                    )

            elif key == "target_scene_id":
                if value is not None and str(value) not in scenes_dict:
                    return json.dumps(
                        {"success": False, "error": f"Scene not found: '{value}'"}
                    )

            elif key == "target_notification_id":
                if value is not None and str(value) not in notifications_dict:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Notification not found: '{value}'",
                        }
                    )

            elif key not in [
                "action_type",
                "target_device_id",
                "target_scene_id",
                "target_notification_id",
            ]:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid update field: '{key}'. Allowed fields: action_type, target_device_id, target_scene_id, target_notification_id",
                    }
                )

        # Determine final values after update
        new_action_type = updates.get("action_type", action_data.get("action_type"))

        final_target_device_id = (
            updates.get("target_device_id")
            if "target_device_id" in updates
            else action_data.get("target_device_id")
        )
        final_target_scene_id = (
            updates.get("target_scene_id")
            if "target_scene_id" in updates
            else action_data.get("target_scene_id")
        )
        final_target_notification_id = (
            updates.get("target_notification_id")
            if "target_notification_id" in updates
            else action_data.get("target_notification_id")
        )

        # Validation rules (same as AddRoutineAction)
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
            "power_outlet": {"power": ["on", "off"], "power_consumption": (0, 3680)},
            "air_conditioner": {
                "power": ["on", "off"],
                "mode": ["cooling", "idle"],
                "temperature": (32, 104),
                "target_temperature": (60, 85),
            },
        }

        # Validate consistency between action_type and targets
        if new_action_type == "device_control":
            if final_target_device_id is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "action_type 'device_control' requires target_device_id to be set",
                    }
                )

            # Validate device exists and get device type
            device = devices_dict.get(str(final_target_device_id))
            if not device:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device not found: '{final_target_device_id}'",
                    }
                )

            device_type = device.get("device_type")
            rules = validation_rules.get(device_type)
            if not rules:
                return json.dumps(
                    {"success": False, "error": f"Unknown device type '{device_type}'"}
                )

        elif new_action_type == "scene_activation":
            if final_target_scene_id is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "action_type 'scene_activation' requires target_scene_id to be set",
                    }
                )
            # Clear device and notification targets if switching to scene_activation
            if "action_type" in updates:
                if "target_device_id" not in updates:
                    updates["target_device_id"] = None
                if "target_notification_id" not in updates:
                    updates["target_notification_id"] = None

        elif new_action_type == "notification":
            if final_target_notification_id is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "action_type 'notification' requires target_notification_id to be set",
                    }
                )
            # Clear device and scene targets if switching to notification
            if "action_type" in updates:
                if "target_device_id" not in updates:
                    updates["target_device_id"] = None
                if "target_scene_id" not in updates:
                    updates["target_scene_id"] = None

        # Handle action_attributes if provided
        updated_attributes = []
        if action_attributes:
            # Only process attributes for device_control actions
            if new_action_type != "device_control":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"action_attributes can only be used with device_control actions, not '{new_action_type}'",
                    }
                )

            device = devices_dict.get(str(final_target_device_id))
            device_type = device.get("device_type")
            rules = validation_rules.get(device_type)

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
            routine_action_attributes = data.get("routine_action_attributes", {})
            timestamp = "2025-12-19T23:59:00"

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

                    # Find existing attribute or create new one
                    existing_attr_id = None
                    for attr_id, attr in routine_action_attributes.items():
                        if (
                            str(attr.get("action_id")) == action_id_str
                            and attr.get("attribute_name") == attr_name
                        ):
                            existing_attr_id = attr_id
                            break

                    if existing_attr_id:
                        # Update existing attribute
                        routine_action_attributes[existing_attr_id][
                            "attribute_value"
                        ] = attr_val
                        routine_action_attributes[existing_attr_id][
                            "updated_at"
                        ] = timestamp
                        updated_attributes.append(
                            routine_action_attributes[existing_attr_id]
                        )
                    else:
                        # Create new attribute
                        next_attr_id = str(generate_id(routine_action_attributes))
                        new_attribute = {
                            "attribute_id": next_attr_id,
                            "action_id": action_id_str,
                            "attribute_name": attr_name,
                            "attribute_value": attr_val,
                            "created_at": timestamp,
                            "updated_at": timestamp,
                        }
                        routine_action_attributes[next_attr_id] = new_attribute
                        updated_attributes.append(new_attribute)

            data["routine_action_attributes"] = routine_action_attributes

        # Apply action updates
        current_time = "2025-12-19T23:59:00"

        for key, value in updates.items():
            action_data[key] = value

        # Always update timestamp
        action_data["updated_at"] = current_time

        return json.dumps(
            {
                "success": True,
                "message": f"Action '{action_id_str}' of routine '{routine_id_str}' updated successfully",
                "action": action_data,
                "attributes": updated_attributes if updated_attributes else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_routine_action",
                "description": (
                    "Update a routine action and optionally its device control attributes. "
                    "Can update action properties (action_type, targets) and/or device attributes in a single call. "
                    "For device_control actions, use action_attributes to update/add attributes. "
                    "Attributes can be passed as a dict {'power': 'on', 'brightness': 75} or list of dicts. "
                    "Existing attributes are updated, new ones are created. "
                    "Validates all changes against device type rules. "
                    "Cannot update action_id, routine_id, or created_at."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine (required).",
                        },
                        "action_id": {
                            "type": "string",
                            "description": "The ID of the action to update (required).",
                        },
                        "updates": {
                            "type": "object",
                            "description": "Dictionary of action fields to update. Allowed: action_type, target_device_id, target_scene_id, target_notification_id.",
                            "properties": {
                                "action_type": {
                                    "type": "string",
                                    "description": "The type of action: 'device_control', 'scene_activation', or 'notification'",
                                },
                                "target_device_id": {
                                    "type": "string",
                                    "description": "The ID of the device to control (required for device_control)",
                                },
                                "target_scene_id": {
                                    "type": "string",
                                    "description": "The ID of the scene to activate (required for scene_activation)",
                                },
                                "target_notification_id": {
                                    "type": "string",
                                    "description": "The ID of the notification to send (required for notification)",
                                },
                            },
                        },
                        "action_attributes": {
                            "type": "object",
                            "description": "For device_control actions: dict or list of dicts containing device attributes to update or add. Each dict can contain multiple attributes as direct key-value pairs. Examples: {'power': 'on', 'brightness': 75} or [{'power': 'on'}, {'temperature': 72}]. Existing attributes are updated, new ones are created. Not used for other action types.",
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
                    "required": ["routine_id", "action_id", "updates"],
                },
            },
        }
