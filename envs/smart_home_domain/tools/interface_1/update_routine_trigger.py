import json
from typing import Any, Dict, Optional, List, Union
from tau_bench.envs.tool import Tool


class UpdateRoutineTrigger(Tool):
    """
    Update a routine trigger and its attributes with comprehensive validation.
    - Can update trigger properties (trigger_type, device_id, solar_event, etc.)
    - Can update device state attributes via trigger_attributes parameter
    - Validates device type and attributes for device_state triggers
    - Updates the 'updated_at' timestamp automatically
    - Cannot update trigger_id, routine_id, or created_at
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        routine_id: str,
        trigger_id: str,
        updates: Dict[str, Any],
        trigger_attributes: Optional[
            Union[Dict[str, Any], List[Dict[str, Any]]]
        ] = None,
    ) -> str:
        """
        Update a routine trigger and optionally its attributes.

        Args:
            data: The data dictionary containing routines and routine_triggers
            routine_id: The ID of the routine
            trigger_id: The ID of the trigger to update
            updates: Dictionary of trigger fields to update
            trigger_attributes: Optional dict or list of dicts with attributes to update/add

        Returns:
            JSON string with success status and updated trigger information
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

        routine_triggers_dict = data.get("routine_triggers", {})
        if not isinstance(routine_triggers_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routine_triggers container: expected dict at data['routine_triggers']",
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

        # Validate required fields
        if routine_id is None:
            return json.dumps({"success": False, "error": "routine_id is required"})

        if trigger_id is None:
            return json.dumps({"success": False, "error": "trigger_id is required"})

        if not isinstance(updates, dict):
            return json.dumps(
                {"success": False, "error": "updates must be a dictionary"}
            )

        if not updates and not trigger_attributes:
            return json.dumps(
                {
                    "success": False,
                    "error": "Either updates or trigger_attributes must be provided",
                }
            )

        # Convert to strings for consistent comparison
        routine_id_str = str(routine_id)
        trigger_id_str = str(trigger_id)

        # Validate routine exists
        if routine_id_str not in routines_dict:
            return json.dumps(
                {"success": False, "error": f"Routine not found: '{routine_id_str}'"}
            )

        # Validate trigger exists
        if trigger_id_str not in routine_triggers_dict:
            return json.dumps(
                {"success": False, "error": f"Trigger not found: '{trigger_id_str}'"}
            )

        trigger_data = routine_triggers_dict[trigger_id_str]

        # Validate trigger belongs to the specified routine
        if str(trigger_data.get("routine_id")) != routine_id_str:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Trigger '{trigger_id_str}' does not belong to routine '{routine_id_str}'",
                }
            )

        # Validate that protected fields are not in updates
        protected_fields = ["trigger_id", "routine_id", "created_at"]
        for field in protected_fields:
            if field in updates:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot update protected field: '{field}'",
                    }
                )

        # Valid trigger types
        valid_trigger_types = ["time_based", "solar_event", "device_state", "manual"]

        # Validate updates values
        for key, value in updates.items():
            if key == "trigger_type":
                if value not in valid_trigger_types:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid trigger_type: '{value}'. Must be one of {valid_trigger_types}",
                        }
                    )

            elif key == "device_id":
                if value is not None and str(value) not in devices_dict:
                    return json.dumps(
                        {"success": False, "error": f"Device not found: '{value}'"}
                    )

            elif key == "solar_event":
                if value is not None and value not in ["sunrise", "sunset"]:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid solar_event: '{value}'. Must be 'sunrise' or 'sunset'",
                        }
                    )

            elif key == "routine_schedule_id":
                # Allow any schedule_id value (including None)
                pass

            elif key not in [
                "trigger_type",
                "device_id",
                "solar_event",
                "routine_schedule_id",
            ]:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid update field: '{key}'. Allowed fields: trigger_type, device_id, solar_event, routine_schedule_id",
                    }
                )

        # Determine final values after update
        new_trigger_type = updates.get("trigger_type", trigger_data.get("trigger_type"))
        final_device_id = (
            updates.get("device_id")
            if "device_id" in updates
            else trigger_data.get("device_id")
        )
        final_solar_event = (
            updates.get("solar_event")
            if "solar_event" in updates
            else trigger_data.get("solar_event")
        )

        # Validation rules (same as AddRoutineTrigger)
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

        # Validate consistency between trigger_type and related fields
        if new_trigger_type == "device_state":
            if final_device_id is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "trigger_type 'device_state' requires device_id to be set",
                    }
                )

            # Validate device exists and get device type
            device = devices_dict.get(str(final_device_id))
            if not device:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device not found: '{final_device_id}'",
                    }
                )

            device_type = device.get("device_type")
            rules = validation_rules.get(device_type)
            if not rules:
                return json.dumps(
                    {"success": False, "error": f"Unknown device type '{device_type}'"}
                )

        elif new_trigger_type == "solar_event":
            if final_solar_event is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "trigger_type 'solar_event' requires solar_event to be set",
                    }
                )
            # Clear device_id if switching to solar_event
            if "trigger_type" in updates and "device_id" not in updates:
                updates["device_id"] = None

        elif new_trigger_type == "time_based":
            # Clear device_id and solar_event if switching to time_based
            if "trigger_type" in updates:
                if "device_id" not in updates:
                    updates["device_id"] = None
                if "solar_event" not in updates:
                    updates["solar_event"] = None

        elif new_trigger_type == "manual":
            # Clear device_id and solar_event if switching to manual
            if "trigger_type" in updates:
                if "device_id" not in updates:
                    updates["device_id"] = None
                if "solar_event" not in updates:
                    updates["solar_event"] = None

        # Handle trigger_attributes if provided
        updated_attributes = []
        if trigger_attributes:
            # Only process attributes for device_state triggers
            if new_trigger_type != "device_state":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"trigger_attributes can only be used with device_state triggers, not '{new_trigger_type}'",
                    }
                )

            device = devices_dict.get(str(final_device_id))
            device_type = device.get("device_type")
            rules = validation_rules.get(device_type)

            # Normalize to list
            if isinstance(trigger_attributes, dict):
                attrs_to_process = [trigger_attributes]
            elif isinstance(trigger_attributes, list):
                attrs_to_process = trigger_attributes
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": "trigger_attributes must be a dict or list of dicts",
                    }
                )

            # Process each attribute dict
            routine_trigger_attributes = data.get("routine_trigger_attributes", {})
            timestamp = "2025-12-19T23:59:00"
            valid_operators = [
                "equals",
                "greater_than",
                "less_than",
                "greater_equal",
                "less_equal",
            ]

            for attr_dict in attrs_to_process:
                if not isinstance(attr_dict, dict):
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Each item in trigger_attributes must be a dict",
                        }
                    )

                # Get comparison_operator if present
                comparison_op = attr_dict.get("comparison_operator")
                if comparison_op and comparison_op not in valid_operators:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid comparison_operator: '{comparison_op}'. Must be one of {valid_operators}",
                        }
                    )

                # Find the attribute name and value (excluding comparison_operator)
                attr_pairs = {
                    k: v for k, v in attr_dict.items() if k != "comparison_operator"
                }

                if len(attr_pairs) == 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "No attribute specified in trigger_attributes",
                        }
                    )
                elif len(attr_pairs) > 1:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Only one attribute can be specified per dict in trigger_attributes",
                        }
                    )

                attr_name, attr_val = next(iter(attr_pairs.items()))

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
                for attr_id, attr in routine_trigger_attributes.items():
                    if (
                        str(attr.get("trigger_id")) == trigger_id_str
                        and attr.get("attribute_name") == attr_name
                    ):
                        existing_attr_id = attr_id
                        break

                if existing_attr_id:
                    # Update existing attribute
                    routine_trigger_attributes[existing_attr_id][
                        "attribute_value"
                    ] = attr_val
                    if comparison_op is not None:
                        routine_trigger_attributes[existing_attr_id][
                            "comparison_operator"
                        ] = comparison_op
                    routine_trigger_attributes[existing_attr_id][
                        "updated_at"
                    ] = timestamp
                    updated_attributes.append(
                        routine_trigger_attributes[existing_attr_id]
                    )
                else:
                    # Create new attribute
                    next_attr_id = str(generate_id(routine_trigger_attributes))
                    new_attribute = {
                        "attribute_id": next_attr_id,
                        "routine_id": routine_id_str,
                        "trigger_id": trigger_id_str,
                        "attribute_name": attr_name,
                        "attribute_value": attr_val,
                        "comparison_operator": comparison_op,
                        "created_at": timestamp,
                        "updated_at": timestamp,
                    }
                    routine_trigger_attributes[next_attr_id] = new_attribute
                    updated_attributes.append(new_attribute)

            data["routine_trigger_attributes"] = routine_trigger_attributes

        # Apply trigger updates
        current_time = "2025-12-19T23:59:00"

        for key, value in updates.items():
            trigger_data[key] = value

        # Always update timestamp
        trigger_data["updated_at"] = current_time

        return json.dumps(
            {
                "success": True,
                "message": f"Trigger '{trigger_id_str}' of routine '{routine_id_str}' updated successfully",
                "trigger": trigger_data,
                "attributes": updated_attributes if updated_attributes else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_routine_trigger",
                "description": (
                    "Update a routine trigger and optionally its device state attributes. "
                    "Can update trigger properties (trigger_type, device_id, solar_event, routine_schedule_id) and/or device attributes in a single call. "
                    "For device_state triggers, use trigger_attributes to update/add attributes. "
                    "Attributes can be passed as a dict {'temperature': 75, 'comparison_operator': 'greater_than'} or list of dicts. "
                    "Each dict must contain exactly one attribute plus optional comparison_operator. "
                    "Existing attributes are updated, new ones are created. "
                    "Validates all changes against device type rules. "
                    "Cannot update trigger_id, routine_id, or created_at."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine (required).",
                        },
                        "trigger_id": {
                            "type": "string",
                            "description": "The ID of the trigger to update (required).",
                        },
                        "updates": {
                            "type": "object",
                            "description": "Dictionary of trigger fields to update. Allowed: trigger_type, device_id, solar_event, routine_schedule_id.",
                            "properties": {
                                "trigger_type": {
                                    "type": "string",
                                    "description": "The type of trigger: 'time_based', 'solar_event', 'device_state', or 'manual'",
                                },
                                "device_id": {
                                    "type": "string",
                                    "description": "The ID of the device (required for device_state triggers)",
                                },
                                "solar_event": {
                                    "type": "string",
                                    "description": "The solar event: 'sunrise' or 'sunset' (required for solar_event triggers)",
                                },
                                "routine_schedule_id": {
                                    "type": "string",
                                    "description": "The ID of the schedule (for time_based triggers)",
                                },
                            },
                        },
                        "trigger_attributes": {
                            "type": "object",
                            "description": "For device_state triggers: dict or list of dicts. Each dict contains one attribute as key and its value, plus optional comparison_operator. Examples: {'temperature': 75, 'comparison_operator': 'greater_than'} or [{'power': 'on'}, {'brightness': 80}]. Existing attributes are updated, new ones are created.",
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
                                "comparison_operator": {
                                    "type": "string",
                                    "description": "Comparison operator: 'equals', 'greater_than', 'less_than', 'greater_equal', or 'less_equal'",
                                },
                            },
                        },
                    },
                    "required": ["routine_id", "trigger_id", "updates"],
                },
            },
        }
