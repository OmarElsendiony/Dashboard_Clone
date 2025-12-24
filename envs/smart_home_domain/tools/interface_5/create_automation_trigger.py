import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateAutomationTrigger(Tool):
    """
    Create a trigger for an automation .
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        automation_id: str,
        trigger_type: str,
        schedule_days: Optional[Dict[str, bool]] = None,
        onset_time: Optional[str] = None,
        frequency: Optional[str] = None,
        solar_event: Optional[str] = None,
        accessory_name: Optional[str] = None,
        attribute_name: Optional[str] = None,
        attribute_value: Optional[str] = None,
        comparison_operator: Optional[str] = None,
    ) -> str:
        """
        Add a trigger to an automation with SOP-style parameters.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        def validate_attribute(device_type: Any, attribute_name: Any, attribute_value: Any, *, allow_readonly: bool) -> (bool, str | None):
            import re

            DEVICE_ATTRIBUTES = {
                "camera": {
                    "power": {"type": "enum", "values": ["on", "off"]},
                    "recording": {"type": "enum", "values": ["recording", "paused", "stopped"]},
                    "motion_detection": {"type": "enum", "values": ["motion_detected", "clear"]},
                },
                "bulb": {
                    "power": {"type": "enum", "values": ["on", "off"]},
                    "brightness": {"type": "numeric", "min": 0, "max": 100, "unit": "%"},
                    "color": {"type": "string", "format": "hex or color_name", "examples": ["#FF0000", "red", "blue", "white"]},
                },
                "thermostat": {
                    "power": {"type": "enum", "values": ["on", "off"]},
                    "mode": {"type": "enum", "values": ["heating", "cooling", "idle"]},
                    "temperature": {"type": "numeric", "min": 32, "max": 104, "unit": "°F"},
                    "target_temperature": {"type": "numeric", "min": 60, "max": 90, "unit": "°F"},
                },
                "speaker": {
                    "power": {"type": "enum", "values": ["on", "off"]},
                    "playback_state": {"type": "enum", "values": ["playing", "paused", "stopped"]},
                    "volume": {"type": "numeric", "min": 0, "max": 100, "unit": "%"},
                    "mute": {"type": "enum", "values": ["muted", "unmuted"]},
                },
                "door_lock": {
                    "lock_state": {"type": "enum", "values": ["locked", "unlocked"]},
                },
                "motion_sensor": {
                    "motion_state": {"type": "enum", "values": ["motion_detected", "clear"], "readonly": True},
                },
                "temperature_sensor": {
                    "temperature": {"type": "numeric", "min": 32, "max": 104, "unit": "°F", "readonly": True},
                },
                "humidity_sensor": {
                    "humidity": {"type": "numeric", "min": 0, "max": 100, "unit": "%", "readonly": True},
                },
                "light_sensor": {
                    "brightness_level": {"type": "numeric", "min": 0, "max": 65535, "unit": "lux", "readonly": True},
                },
                "door_sensor": {
                    "door_state": {"type": "enum", "values": ["open", "closed"], "readonly": True},
                },
                "water_leak_sensor": {
                    "leak_state": {"type": "enum", "values": ["leak_detected", "no_leak"], "readonly": True},
                },
                "smoke_detector_sensor": {
                    "smoke_state": {"type": "enum", "values": ["smoke_detected", "no_smoke", "alarm_triggered"], "readonly": True},
                },
                "power_outlet": {
                    "power": {"type": "enum", "values": ["on", "off"]},
                    "power_consumption": {"type": "numeric", "min": 0, "max": 3680, "unit": "watts"},
                },
                "air_conditioner": {
                    "power": {"type": "enum", "values": ["on", "off"]},
                    "mode": {"type": "enum", "values": ["cooling", "idle"]},
                    "temperature": {"type": "numeric", "min": 32, "max": 104, "unit": "°F"},
                    "target_temperature": {"type": "numeric", "min": 60, "max": 85, "unit": "°F"},
                },
            }

            if not isinstance(device_type, str) or not device_type.strip():
                return False, "Invalid accessory type"
            dt = device_type.strip()

            if not isinstance(attribute_name, str) or not attribute_name.strip():
                return False, "attribute_name must be provided"
            name = attribute_name.strip()

            if not isinstance(attribute_value, str) or not attribute_value.strip():
                return False, "attribute_value must be provided"
            val = attribute_value.strip()

            rules_for_type = DEVICE_ATTRIBUTES.get(dt)
            if not rules_for_type:
                return False, "Invalid accessory type"

            rule = rules_for_type.get(name)
            if not rule:
                return False, f"Invalid command for {dt}"

            if rule.get("readonly") and not allow_readonly:
                return False, f"Attribute '{name}' is read-only for {dt}"

            rtype = rule.get("type")
            if rtype == "enum":
                if val not in set(rule.get("values") or []):
                    return False, f"Invalid value for {dt} {name}"
                return True, None

            if rtype == "numeric":
                try:
                    num = float(val)
                except Exception:
                    return False, f"Invalid value for {dt} {name}"
                min_v = rule.get("min")
                max_v = rule.get("max")
                if min_v is not None and num < float(min_v):
                    return False, f"Invalid value for {dt} {name}"
                if max_v is not None and num > float(max_v):
                    return False, f"Invalid value for {dt} {name}"
                return True, None

            if rtype == "string":
                if rule.get("format") == "hex or color_name" and val.startswith("#"):
                    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", val):
                        return False, f"Invalid value for {dt} {name}"
                return True, None

            return False, f"Invalid command for {dt}"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        routines = data.get("routines")
        devices = data.get("devices")
        routine_triggers = data.get("routine_triggers")
        routine_schedule = data.get("routine_schedules")
        routine_trigger_attributes = data.get("routine_trigger_attributes")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(routines, dict):
            return json.dumps({"success": False, "error": "routines store missing"})
        if not isinstance(routine_triggers, dict):
            return json.dumps({"success": False, "error": "routine_triggers store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        for hid, home in homes.items():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                break
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        if not isinstance(automation_id, str) or not automation_id.strip():
            return json.dumps({"success": False, "error": "automation_id must be provided"})
        automation_id = automation_id.strip()

        if automation_id not in routines:
            return json.dumps({"success": False, "error": f"Automation '{automation_id}' not found"})

        if routines[automation_id].get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Automation '{automation_id}' does not belong to home '{home_name}'"})

        if not isinstance(trigger_type, str) or not trigger_type.strip():
            return json.dumps({"success": False, "error": "trigger_type must be provided"})
        trigger_type = trigger_type.strip().lower()

        allowed_types = {"time_based", "solar_event", "device_state", "manual"}
        if trigger_type not in allowed_types:
            return json.dumps({"success": False, "error": f"trigger_type must be one of {', '.join(allowed_types)}"})

        schedule_id = None
        if trigger_type == "time_based":
            if not isinstance(routine_schedule, dict):
                return json.dumps({"success": False, "error": "routine_schedule store missing"})

            if not isinstance(onset_time, str) or not onset_time.strip():
                return json.dumps({"success": False, "error": "onset_time must be provided for time_based triggers"})
            onset = onset_time.strip()
            
            # Validate and parse schedule_days
            if not schedule_days or not isinstance(schedule_days, dict):
                return json.dumps({"success": False, "error": "schedule_days must be provided as a dictionary for time_based triggers"})
            
            allowed_days = {"on_monday", "on_tuesday", "on_wednesday", "on_thursday", "on_friday", "on_saturday", "on_sunday"}
            
            # Validate keys
            for key in schedule_days.keys():
                if key not in allowed_days:
                    return json.dumps({"success": False, "error": f"Invalid day key '{key}'. Allowed keys: {', '.join(allowed_days)}"})
            
            # Check if at least one day is True
            if not any(schedule_days.get(day, False) for day in allowed_days):
                return json.dumps({"success": False, "error": "At least one day must be set to True in schedule_days"})
            
            schedule_id = generate_id(routine_schedule)
            schedule_record = {
                "schedule_id": schedule_id,
                "routine_id": automation_id,
                "on_monday": bool(schedule_days.get("on_monday", False)),
                "on_tuesday": bool(schedule_days.get("on_tuesday", False)),
                "on_wednesday": bool(schedule_days.get("on_wednesday", False)),
                "on_thursday": bool(schedule_days.get("on_thursday", False)),
                "on_friday": bool(schedule_days.get("on_friday", False)),
                "on_saturday": bool(schedule_days.get("on_saturday", False)),
                "on_sunday": bool(schedule_days.get("on_sunday", False)),
                "onset_time": onset,
                "frequency": frequency.strip() if isinstance(frequency, str) and frequency.strip() else None,
            }
            routine_schedule[schedule_id] = schedule_record

        solar_val = None
        if trigger_type == "solar_event":
            if not solar_event:
                return json.dumps({"success": False, "error": "solar_event is required for solar_event triggers"})
            solar_val = solar_event.strip().lower()
            if solar_val not in {"sunrise", "sunset"}:
                return json.dumps({"success": False, "error": "solar_event must be one of sunrise, sunset"})

        device_val = None
        if trigger_type == "device_state":
            if not isinstance(devices, dict):
                return json.dumps({"success": False, "error": "devices store missing"})
            if not isinstance(accessory_name, str) or not accessory_name.strip():
                return json.dumps({"success": False, "error": "accessory_name is required for device_state triggers"})
            if not isinstance(attribute_name, str) or not attribute_name.strip():
                return json.dumps({"success": False, "error": "attribute_name is required for device_state triggers"})
            if attribute_value is None or (isinstance(attribute_value, str) and not attribute_value.strip()):
                return json.dumps({"success": False, "error": "attribute_value is required for device_state triggers"})

            name_val = accessory_name.strip().lower()
            matches = []
            for did, dev in devices.items():
                if dev.get("home_id") == home_id and dev.get("device_name", "").strip().lower() == name_val:
                    matches.append(did)
            if not matches:
                return json.dumps({"success": False, "error": f"Accessory '{accessory_name.strip()}' not found in home '{home_name}'"})
            if len(matches) > 1:
                return json.dumps({"success": False, "error": f"Multiple accessories named '{accessory_name.strip()}' found in home '{home_name}'"})
            device_val = matches[0]

            # Enforce attribute/value constraints for this device type (readonly allowed for triggers)
            device = devices.get(device_val, {})
            ok, err = validate_attribute(device.get("device_type"), str(attribute_name), str(attribute_value), allow_readonly=True)
            if not ok:
                return json.dumps({"success": False, "error": err})

            op = None
            if comparison_operator is not None:
                if not isinstance(comparison_operator, str):
                    return json.dumps({"success": False, "error": "comparison_operator must be a string"})
                op = comparison_operator.strip().lower()
                allowed_ops = {"equals","greater_than","less_than","greater_equal","less_equal"}
                if op not in allowed_ops:
                    return json.dumps({"success": False, "error": "comparison_operator must be one of equals, greater_than, less_than, greater_equal, less_equal"})

        trigger_id = generate_id(routine_triggers)
        timestamp = "2025-12-19T23:59:00"

        trigger_record = {
            "trigger_id": trigger_id,
            "routine_id": automation_id,
            "trigger_type": trigger_type,
            "routine_schedule_id": schedule_id,
            "solar_event": solar_val,
            "device_id": device_val,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routine_triggers[trigger_id] = trigger_record

        attribute_records = []
        if trigger_type == "device_state":
            if not isinstance(routine_trigger_attributes, dict):
                return json.dumps({"success": False, "error": "routine_trigger_attributes store missing"})
            attr_id = generate_id(routine_trigger_attributes)
            attr_record = {
                "attribute_id": attr_id,
                "trigger_id": trigger_id,
                "attribute_name": str(attribute_name).strip(),
                "attribute_value": str(attribute_value).strip() if isinstance(attribute_value, str) else str(attribute_value),
                "comparison_operator": op,
                "created_at": timestamp,
            }
            routine_trigger_attributes[attr_id] = attr_record
            attribute_records.append(attr_record)

        return json.dumps({
            "success": True,
            "trigger": {
                "trigger_id": trigger_record.get("trigger_id"),
                "automation_id": trigger_record.get("routine_id"),
                "trigger_type": trigger_record.get("trigger_type"),
                "schedule_id": trigger_record.get("routine_schedule_id"),
                "solar_event": trigger_record.get("solar_event"),
                "accessory_id": trigger_record.get("device_id"),
                "created_at": trigger_record.get("created_at"),
                "updated_at": trigger_record.get("updated_at"),
            },
            "attributes": (
                None
                if not attribute_records
                else [
                    {
                        "attribute_name": a.get("attribute_name"),
                        "attribute_value": a.get("attribute_value"),
                        "comparison_operator": a.get("comparison_operator"),
                        "created_at": a.get("created_at"),
                    }
                    for a in attribute_records
                ]
            ),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_automation_trigger",
                "description": "Create a trigger for an automation. Defines when the automation should be activated. Supports time-based (scheduled), solar event (sunrise/sunset), accessory state (sensor/accessory changes), and manual triggers. Accessory attributes are validated based on accessory type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "automation_id": {
                            "type": "string",
                            "description": "Identifier of the automation.",
                        },
                        "trigger_type": {
                            "type": "string",
                            "description": "Type of trigger; allowed values: time_based, solar_event, device_state, manual.",
                        },
                        "schedule_days": {
                            "type": "object",
                            "description": "Dictionary specifying which days the trigger should run. Required for time_based triggers. Keys: on_monday, on_tuesday, on_wednesday, on_thursday, on_friday, on_saturday, on_sunday. Values: True/False. At least one day must be True. Example: {\"on_monday\": true, \"on_wednesday\": true, \"on_friday\": true}",
                            "properties": {
                                "on_monday": {
                                    "type": "boolean",
                                    "description": "Schedule trigger for Monday (True/False). For time_based triggers.",
                                },
                                "on_tuesday": {
                                    "type": "boolean",
                                    "description": "Schedule trigger for Tuesday (True/False). For time_based triggers.",
                                },
                                "on_wednesday": {
                                    "type": "boolean",
                                    "description": "Schedule trigger for Wednesday (True/False). For time_based triggers.",
                                },
                                "on_thursday": {
                                    "type": "boolean",
                                    "description": "Schedule trigger for Thursday (True/False). For time_based triggers.",
                                },
                                "on_friday": {"type": "boolean",
                                    "description": "Schedule trigger for Friday (True/False). For time_based triggers.",
                                },
                                "on_saturday": {"type": "boolean",
                                    "description": "Schedule trigger for Saturday (True/False). For time_based triggers.",
                                },
                                "on_sunday": {"type": "boolean",
                                    "description": "Schedule trigger for Sunday (True/False). For time_based triggers.",
                                },
                            }
                        },
                        "solar_event": {
                            "type": "string",
                            "description": "Solar event for solar_event triggers; allowed values: sunrise, sunset.",
                        },
                        "onset_time": {
                            "type": "string",
                            "description": "Onset time for time_based triggers (e.g., 'HH:MM:SS'). Required for time_based triggers.",
                        },
                        "frequency": {
                            "type": "string",
                            "description": "Optional frequency for time_based triggers (e.g., daily, weekly).",
                        },
                        "accessory_name": {
                            "type": "string",
                            "description": "Accessory name for device_state triggers.",
                        },
                        "attribute_name": {
                            "type": "string",
                            "description": "Attribute name for device_state triggers.",
                        },
                        "attribute_value": {
                            "type": "string",
                            "description": "Attribute value for device_state triggers.",
                        },
                        "comparison_operator": {
                            "type": "string",
                            "description": "Optional comparison operator for device_state triggers; allowed values: equals, greater_than, less_than, greater_equal, less_equal.",
                        },
                    },
                    "required": ["home_name", "automation_id", "trigger_type"],
                },
            },
        }

