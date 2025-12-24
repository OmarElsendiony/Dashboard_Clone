import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListAccessories(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        room_id: Optional[str] = None,
        accessory_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        List accessories in a home with optional filters.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        devices = data.get("devices")

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

        room_filter = room_id.strip() if isinstance(room_id, str) and room_id.strip() else None
        
        type_filter = None
        if accessory_type:
            if not isinstance(accessory_type, str):
                return json.dumps({"success": False, "error": "accessory_type must be a string"})
            type_filter = accessory_type.strip().lower()
            allowed_types = {"camera", "bulb", "thermostat", "speaker", "door_lock", "motion_sensor", "temperature_sensor", "humidity_sensor", "light_sensor", "door_sensor", "water_leak_sensor", "smoke_detector_sensor", "power_outlet", "air_conditioner"}
            if type_filter not in allowed_types:
                return json.dumps({"success": False, "error": f"accessory_type must be one of {', '.join(allowed_types)}"})

        status_filter = None
        if status:
            if not isinstance(status, str):
                return json.dumps({"success": False, "error": "status must be a string"})
            status_filter = status.strip().lower()
            if status_filter not in {"online", "offline"}:
                return json.dumps({"success": False, "error": "status must be one of online, offline"})

        result_accessories = []
        for device_id, device in devices.items():
            if device.get("home_id") == home_id:
                if room_filter and device.get("room_id") != room_filter:
                    continue
                if type_filter and device.get("device_type") != type_filter:
                    continue
                if status_filter and device.get("status") != status_filter:
                    continue
                # Return SOP terminology only (do not leak DB field names)
                result_accessories.append({
                    "accessory_id": device.get("device_id") or device_id,
                    "accessory_name": device.get("device_name"),
                    "accessory_type": device.get("device_type"),
                    "room_id": device.get("room_id"),
                    "serial_number": device.get("serial_number"),
                    "status": device.get("status"),
                    "support_automation": device.get("support_automation"),
                    "installed_at": device.get("installed_at"),
                    "last_seen": device.get("last_seen"),
                    "created_at": device.get("created_at"),
                    "updated_at": device.get("updated_at"),
                })

        return json.dumps({"success": True, "accessories": result_accessories})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_accessories",
                "description": "List all accessories in a home with optional filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Optional room filter.",
                        },
                        "accessory_type": {
                            "type": "string",
                            "description": "Optional accessory type filter; allowed values: camera, bulb, thermostat, speaker, door_lock, motion_sensor, temperature_sensor, humidity_sensor, light_sensor, door_sensor, water_leak_sensor, smoke_detector_sensor, power_outlet, air_conditioner.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter; allowed values: online, offline.",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }

