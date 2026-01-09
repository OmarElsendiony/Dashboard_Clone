import json
from typing import Any, Dict, Optional, List, Union
from tau_bench.envs.tool import Tool


class AddRoutineTrigger(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        trigger_type: str,
        trigger_attributes: Optional[
            Union[Dict[str, Any], List[Dict[str, Any]]]
        ] = None,
        routine_id: Optional[str] = None,
        routine_name: Optional[str] = None,
        schedule_id: Optional[str] = None,
        solar_event: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        # 1. Routine Validation
        routines = data.get("routines", {})
        if routine_name and not routine_id:
            for rid, routine in routines.items():
                if (
                    routine.get("routine_name", "").strip().lower()
                    == routine_name.strip().lower()
                ):
                    routine_id = rid
                    break

        if not routine_id or routine_id not in routines:
            return json.dumps({"success": False, "error": "Routine not found"})

        # 2. Trigger Type Validation
        valid_trigger_types = ["time_based", "solar_event", "device_state", "manual"]
        if trigger_type not in valid_trigger_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid trigger type. Must be one of {valid_trigger_types}",
                }
            )

        # 3. Solar Event Validation
        if trigger_type == "solar_event":
            if solar_event not in ["sunrise", "sunset"]:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid solar event. Use 'sunrise' or 'sunset'",
                    }
                )

        # 4. Device and Attribute Validation
        attribute_list = []

        if trigger_type == "device_state":
            if not device_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "device_id is required for device_state triggers",
                    }
                )

            devices = data.get("devices", {})
            device = devices.get(device_id)
            if not device:
                return json.dumps({"success": False, "error": "Device not found"})

            device_type = device.get("device_type")

            # Define validation rules based on description
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

            # Normalize trigger_attributes to a list of dicts
            if trigger_attributes:
                if isinstance(trigger_attributes, dict):
                    # Single dict: convert to list
                    attrs_to_process = [trigger_attributes]
                elif isinstance(trigger_attributes, list):
                    # Already a list
                    attrs_to_process = trigger_attributes
                else:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "trigger_attributes must be a dict or list of dicts",
                        }
                    )
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": "trigger_attributes required for device_state triggers",
                    }
                )

            # Process each attribute dict
            for attr_dict in attrs_to_process:
                if not isinstance(attr_dict, dict):
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Each item in trigger_attributes must be a dict",
                        }
                    )

                # Extract comparison_operator once per dict (applies to all attributes in that dict)
                comparison_op = attr_dict.get("comparison_operator")

                # Process all attributes in this dict (excluding comparison_operator)
                for attr_name, attr_val in attr_dict.items():
                    if attr_name == "comparison_operator":
                        continue

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
                        {
                            "attribute_name": attr_name,
                            "attribute_value": attr_val,
                            "comparison_operator": comparison_op,
                        }
                    )

        # 5. Data Persistence
        routine_triggers = data.get("routine_triggers", {})
        next_trigger_id = str(generate_id(routine_triggers))
        timestamp = "2025-12-19T23:59:00"

        trigger = {
            "trigger_id": next_trigger_id,
            "routine_id": routine_id,
            "routine_schedule_id": schedule_id,
            "trigger_type": trigger_type,
            "solar_event": solar_event,
            "device_id": device_id,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routine_triggers[next_trigger_id] = trigger
        data["routine_triggers"] = routine_triggers

        # Save all attributes
        saved_attributes = []
        if attribute_list:
            rt_attrs = data.get("routine_trigger_attributes", {})
            for attr_info in attribute_list:
                next_attr_id = str(generate_id(rt_attrs))
                routine_trigger_attr = {
                    "attribute_id": next_attr_id,
                    "routine_id": routine_id,
                    "trigger_id": next_trigger_id,
                    "attribute_name": attr_info["attribute_name"],
                    "attribute_value": attr_info["attribute_value"],
                    "comparison_operator": attr_info["comparison_operator"],
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                rt_attrs[next_attr_id] = routine_trigger_attr
                saved_attributes.append(routine_trigger_attr)
            data["routine_trigger_attributes"] = rt_attrs

        return json.dumps(
            {
                "success": True,
                "routine_trigger": trigger,
                "attributes": saved_attributes if saved_attributes else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_routine_trigger",
                "description": "Add a trigger to a specified routine in a smart home system. Supports time-based (scheduled), solar event (sunrise/sunset), device state changes, and manual triggers. For device_state triggers, pass attributes directly in trigger_attributes. Can pass a single dict with multiple attributes {'temperature': 75, 'humidity': 60, 'comparison_operator': 'greater_than'} or a list of dicts. The comparison_operator applies to all attributes in the same dict. Device attributes are validated based on device type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to which the trigger will be added.",
                        },
                        "routine_name": {
                            "type": "string",
                            "description": "The name of the routine to which the trigger will be added (used if routine_id is not provided).",
                        },
                        "trigger_type": {
                            "type": "string",
                            "description": "The type of trigger to be added (e.g., time_based, solar_event, device_state, manual).",
                        },
                        "trigger_attributes": {
                            "type": "array",
                            "description": "For device_state triggers: either a single dict or a list of dicts. Each dict can contain multiple attributes. The comparison_operator key in a dict applies to all attributes in that dict. Examples: {'temperature': 75, 'humidity': 60, 'comparison_operator': 'greater_than'} or [{'power': 'on'}, {'brightness': 80, 'comparison_operator': 'equals'}].",
                        },
                        "schedule_id": {
                            "type": "string",
                            "description": "The ID of the schedule associated with the trigger, if applicable.",
                        },
                        "solar_event": {
                            "type": "string",
                            "description": "The solar event associated with the trigger (e.g., sunrise, sunset), if applicable.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device associated with the trigger, if applicable.",
                        },
                    },
                    "required": ["trigger_type"],
                },
            },
        }
