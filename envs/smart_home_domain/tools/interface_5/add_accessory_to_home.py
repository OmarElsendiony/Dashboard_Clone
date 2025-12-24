import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class AddAccessoryToHome(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        accessory_name: str,
        accessory_type: str,
        serial_number: str,
        support_automation: Optional[bool] = False,
        room_id: Optional[str] = None,
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        devices = data.get("devices")
        rooms = data.get("rooms")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(devices, dict):
            return json.dumps({"success": False, "error": "devices store missing"})

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

        if not isinstance(accessory_name, str) or not accessory_name.strip():
            return json.dumps({"success": False, "error": "accessory_name must be provided"})
        accessory_name = accessory_name.strip()

        if not isinstance(accessory_type, str) or not accessory_type.strip():
            return json.dumps({"success": False, "error": "accessory_type must be provided"})
        accessory_type = accessory_type.strip().lower()

        allowed_types = {"camera", "bulb", "thermostat", "speaker", "door_lock", "motion_sensor", "temperature_sensor", "humidity_sensor", "light_sensor", "door_sensor", "water_leak_sensor", "smoke_detector_sensor", "power_outlet", "air_conditioner"}
        if accessory_type not in allowed_types:
            return json.dumps({"success": False, "error": f"accessory_type must be one of {', '.join(allowed_types)}"})

        if not isinstance(serial_number, str) or not serial_number.strip():
            return json.dumps({"success": False, "error": "serial_number must be provided"})
        serial_number = serial_number.strip()

        for device in devices.values():
            if device.get("serial_number") == serial_number:
                return json.dumps({"success": False, "error": f"Device with serial number '{serial_number}' already exists"})

        room_val = None
        if room_id:
            if not isinstance(room_id, str) or not room_id.strip():
                return json.dumps({"success": False, "error": "room_id must be a non-empty string"})
            room_val = room_id.strip()
            if isinstance(rooms, dict) and room_val not in rooms:
                return json.dumps({"success": False, "error": f"Room '{room_val}' not found"})
            if isinstance(rooms, dict) and rooms[room_val].get("home_id") != home_id:
                return json.dumps({"success": False, "error": f"Room '{room_val}' does not belong to home '{home_name}'"})

        automation_support = bool(support_automation)

        device_id = generate_id(devices)
        timestamp = "2025-12-19T23:59:00"

        record = {
            "device_id": device_id,
            "home_id": home_id,
            "room_id": room_val,
            "device_name": accessory_name,
            "device_type": accessory_type,
            "serial_number": serial_number,
            "status": "offline",
            "support_automation": automation_support,
            "installed_at": None,
            "last_seen": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        devices[device_id] = record

        # Return SOP terminology only (do not leak DB field names)
        presented = {
            "accessory_id": record.get("device_id"),
            "accessory_name": record.get("device_name"),
            "accessory_type": record.get("device_type"),
            "room_id": record.get("room_id"),
            "serial_number": record.get("serial_number"),
            "status": record.get("status"),
            "support_automation": record.get("support_automation"),
            "installed_at": record.get("installed_at"),
            "last_seen": record.get("last_seen"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }
        return json.dumps({"success": True, "accessory": presented})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_accessory_to_home",
                "description": "Add a new device to a home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "accessory_name": {
                            "type": "string",
                            "description": "Name of the accessory.",
                        },
                        "accessory_type": {
                            "type": "string",
                            "description": "Type of accessory; allowed values: camera, bulb, thermostat, speaker, door_lock, motion_sensor, temperature_sensor, humidity_sensor, light_sensor, door_sensor, water_leak_sensor, smoke_detector_sensor, power_outlet, air_conditioner.",
                        },
                        "serial_number": {
                            "type": "string",
                            "description": "Unique serial number of the accessory.",
                        },
                        "support_automation": {
                            "type": "boolean",
                            "description": "Whether the accessory supports automation (True/False).",
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Optional room identifier to assign the accessory to.",
                        },
                    },
                    "required": ["home_name", "accessory_name", "accessory_type", "serial_number"],
                },
            },
        }

