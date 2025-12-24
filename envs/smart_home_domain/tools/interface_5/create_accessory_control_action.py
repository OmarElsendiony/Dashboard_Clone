import json
from typing import Any, Dict, Union
from tau_bench.envs.tool import Tool

class CreateAccessoryControlAction(Tool):
    """
    Create an accessory control action for a routine.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        automation_id: str,
        accessory_id: str,
        command: str,
        value: Union[str, int, float],
    ) -> str:
        """
        Add an accessory control action to an automation.
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
                return False, "command must be provided"
            name = attribute_name.strip()

            if attribute_value is None:
                return False, "value must be provided"
            # accept string or numeric; normalize to string for enum/string checks, numeric parsing for numeric rules
            if isinstance(attribute_value, str):
                if not attribute_value.strip():
                    return False, "value must be provided"
                val_str = attribute_value.strip()
                val_num = None
                try:
                    val_num = float(val_str)
                except Exception:
                    val_num = None
            elif isinstance(attribute_value, (int, float)):
                val_num = float(attribute_value)
                # Keep a stable string form for storage/comparisons where needed
                val_str = str(attribute_value)
            else:
                return False, "value must be a string or a number"

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
                if val_str not in set(rule.get("values") or []):
                    return False, f"Invalid value for {dt} {name}"
                return True, None

            if rtype == "numeric":
                if val_num is None:
                    return False, f"Invalid value for {dt} {name}"
                num = float(val_num)
                min_v = rule.get("min")
                max_v = rule.get("max")
                if min_v is not None and num < float(min_v):
                    return False, f"Invalid value for {dt} {name}"
                if max_v is not None and num > float(max_v):
                    return False, f"Invalid value for {dt} {name}"
                return True, None

            if rtype == "string":
                if not isinstance(attribute_value, str):
                    return False, f"Invalid value for {dt} {name}"
                if rule.get("format") == "hex or color_name" and val_str.startswith("#"):
                    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", val_str):
                        return False, f"Invalid value for {dt} {name}"
                return True, None

            return False, f"Invalid command for {dt}"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        routines = data.get("routines")
        devices = data.get("devices")
        routine_actions = data.get("routine_actions")
        routine_action_attributes = data.get("routine_action_attributes")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(routines, dict):
            return json.dumps({"success": False, "error": "routines store missing"})
        if not isinstance(devices, dict):
            return json.dumps({"success": False, "error": "devices store missing"})
        if not isinstance(routine_actions, dict):
            return json.dumps({"success": False, "error": "routine_actions store missing"})
        if not isinstance(routine_action_attributes, dict):
            return json.dumps({"success": False, "error": "routine_action_attributes store missing"})

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

        if not isinstance(accessory_id, str) or not accessory_id.strip():
            return json.dumps({"success": False, "error": "accessory_id must be provided"})
        accessory_id = accessory_id.strip()

        if accessory_id not in devices:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' not found"})
        device = devices[accessory_id]
        if device.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' does not belong to home '{home_name}'"})

        if not isinstance(command, str) or not command.strip():
            return json.dumps({"success": False, "error": "command must be provided"})
        command = command.strip()

        if not isinstance(value, str) or not value.strip():
            if not isinstance(value, (int, float)) and value is not None:
                return json.dumps({"success": False, "error": "value must be provided"})
        if isinstance(value, str):
            if not value.strip():
                return json.dumps({"success": False, "error": "value must be provided"})
            value = value.strip()

        ok, err = validate_attribute(device.get("device_type"), command, value, allow_readonly=False)
        if not ok:
            return json.dumps({"success": False, "error": err})

        action_id = generate_id(routine_actions)
        timestamp = "2025-12-19T23:59:00"

        action_record = {
            "action_id": action_id,
            "routine_id": automation_id,
            "action_type": "accessory_control",
            "target_accessory_id": accessory_id,
            "target_scene_id": None,
            "target_notification_id": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routine_actions[action_id] = action_record

        attribute_records = []
        attr_id = generate_id(routine_action_attributes)
        attr_record = {
            "attribute_id": attr_id,
            "action_id": action_id,
            "attribute_name": str(command),
            # DB stores string; accept numeric at API layer and serialize for storage
            "attribute_value": str(value),
            "created_at": timestamp,
        }
        routine_action_attributes[attr_id] = attr_record
        attribute_records.append(attr_record)

        return json.dumps({
            "success": True,
            "action": {
                "action_id": action_record.get("action_id"),
                "automation_id": action_record.get("routine_id"),
                "action_type": action_record.get("action_type"),
                "accessory_id": action_record.get("target_accessory_id"),
                "created_at": action_record.get("created_at"),
                "updated_at": action_record.get("updated_at"),
            },
            "attributes": [
                {
                    "attribute_name": a.get("attribute_name"),
                    "attribute_value": a.get("attribute_value"),
                    "created_at": a.get("created_at"),
                }
                for a in attribute_records
            ],
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_accessory_control_action",
                "description": "Create an accessory control action for an automation. Controls smart accessories by setting their attributes when the automation is triggered. Accessory attributes are validated based on accessory type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85).",
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
                        "accessory_id": {
                            "type": "string",
                            "description": "Identifier of the accessory to control.",
                        },
                        "command": {
                            "type": "string",
                            "description": "Command/attribute name to set.",
                        },
                        "value": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "number"},
                            ],
                            "description": "Value for the command (string or number depending on the accessory attribute).",
                        },
                    },
                    "required": ["home_name", "automation_id", "accessory_id", "command", "value"],
                },
            },
        }

