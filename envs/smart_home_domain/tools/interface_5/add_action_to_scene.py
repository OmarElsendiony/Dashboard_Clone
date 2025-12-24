import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddActionToScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        scene_id: str,
        accessory_id: str,
        command: str,
        value: str,
    ) -> str:
        """
        Add an accessory control action to a scene with an explicit order.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        def validate_attribute(device_type: Any, attribute_name: Any, attribute_value: Any, *, allow_readonly: bool) -> (bool, str | None):
            # Inline policy: only allow the attributes/values defined by the user. No other attributes accepted.
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

            if not isinstance(attribute_value, str) or not attribute_value.strip():
                return False, "value must be provided"
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
        scenes = data.get("scenes")
        devices = data.get("devices")
        scene_actions = data.get("scene_actions")
        scene_action_attributes = data.get("scene_action_attributes")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(scenes, dict):
            return json.dumps({"success": False, "error": "scenes store missing"})
        if not isinstance(devices, dict):
            return json.dumps({"success": False, "error": "devices store missing"})
        if not isinstance(scene_actions, dict):
            return json.dumps({"success": False, "error": "scene_actions store missing"})
        if not isinstance(scene_action_attributes, dict):
            return json.dumps({"success": False, "error": "scene_action_attributes store missing"})

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

        if not isinstance(scene_id, str) or not scene_id.strip():
            return json.dumps({"success": False, "error": "scene_id must be provided"})
        scene_id = scene_id.strip()

        if scene_id not in scenes:
            return json.dumps({"success": False, "error": f"Scene '{scene_id}' not found"})

        if not isinstance(accessory_id, str) or not accessory_id.strip():
            return json.dumps({"success": False, "error": "accessory_id must be provided"})
        accessory_id = accessory_id.strip()

        if accessory_id not in devices:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' not found"})

        if not isinstance(command, str) or not command.strip():
            return json.dumps({"success": False, "error": "command must be provided"})
        command = command.strip()

        if not isinstance(value, str) or not value.strip():
            return json.dumps({"success": False, "error": "value must be provided"})
        value = value.strip()

        scene = scenes[scene_id]
        device = devices[accessory_id]

        if scene.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Scene '{scene_id}' does not belong to home '{home_name}'"})
        if device.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' does not belong to home '{home_name}'"})

        ok, err = validate_attribute(device.get("device_type"), command, value, allow_readonly=False)
        if not ok:
            return json.dumps({"success": False, "error": err})

        scene_action_id = generate_id(scene_actions)
        timestamp = "2025-12-19T23:59:00"

        action_record = {
            "scene_action_id": scene_action_id,
            "scene_id": scene_id,
            "device_id": accessory_id,
            "created_at": timestamp,
        }
        scene_actions[scene_action_id] = action_record

        attribute_records = []
        attr_id = generate_id(scene_action_attributes)
        attr_record = {
            "attribute_id": attr_id,
            "scene_action_id": scene_action_id,
            "attribute_name": str(command),
            "attribute_value": str(value),
            "created_at": timestamp,
        }
        scene_action_attributes[attr_id] = attr_record
        attribute_records.append(attr_record)

        return json.dumps({
            "success": True,
            "scene_action": {
                "scene_action_id": action_record.get("scene_action_id"),
                "scene_id": action_record.get("scene_id"),
                "accessory_id": action_record.get("device_id"),
                "created_at": action_record.get("created_at"),
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
                "name": "add_action_to_scene",
                "description": "Add an accessory control action to a scene. Device attributes include: camera (power, recording, motion_detection), bulb (power, brightness 0-100%, color), thermostat (power, mode, temperature 32-104°F, target_temperature 60-90°F), speaker (power, playback_state, volume 0-100%, mute), door_lock (lock_state), power_outlet (power, power_consumption 0-3680W), air_conditioner (power, mode, temperature 32-104°F, target_temperature 60-85°F). Sensors are read-only and cannot be controlled in scenes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "scene_id": {
                            "type": "string",
                            "description": "Identifier of the scene.",
                        },
                        "accessory_id": {
                            "type": "string",
                            "description": "Identifier of the accessory to control.",
                        },
                        "command": {
                            "type": "string",
                            "description": "Command/attribute name to set (e.g., power, brightness, target_temperature).",
                        },
                        "value": {
                            "type": "string",
                            "description": "Value for the command.",
                        },
                    },
                    "required": ["home_name", "scene_id", "accessory_id", "command", "value"],
                },
            },
        }

