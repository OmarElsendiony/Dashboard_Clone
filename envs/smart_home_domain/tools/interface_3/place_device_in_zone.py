import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class PlaceDeviceInZone(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        device_id: str,
        zone_id: str,
    ) -> str:
        """
        Assign an existing device to a zone within a household. Validates that the device and zone belong to
        the specified home before updating the device record.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            homes = data.get("homes")
            devices = data.get("devices")
            rooms = data.get("rooms")
            if not isinstance(homes, dict) or not isinstance(devices, dict) or not isinstance(rooms, dict):
                return json.dumps({"success": False, "error": "homes, devices, or rooms table missing/invalid."})

            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps({"success": False, "error": "home_id is required."})
            target_home_id = home_id.strip()
            if target_home_id not in homes:
                return json.dumps({"success": False, "error": "Household not found."})

            if not isinstance(device_id, str) or not device_id.strip():
                return json.dumps({"success": False, "error": "device_id is required."})
            device_record = devices.get(device_id.strip())
            if not isinstance(device_record, dict) or str(device_record.get("home_id")) != target_home_id:
                return json.dumps({"success": False, "error": "Device does not belong to the specified household."})

            if not isinstance(zone_id, str) or not zone_id.strip():
                return json.dumps({"success": False, "error": "zone_id is required."})
            zone_record = rooms.get(zone_id.strip())
            if not isinstance(zone_record, dict) or str(zone_record.get("home_id")) != target_home_id:
                return json.dumps({"success": False, "error": "Zone does not belong to the specified household."})

            device_record["room_id"] = zone_id.strip()
            device_record["updated_at"] = "2025-12-19T23:59:00"
            device_record["zone_id"] = device_record.pop("room_id", None)

            return json.dumps({"success": True, "device": device_record})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"place_device_in_zone failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "place_device_in_zone",
                "description": (
                    "Assign an existing device to a zone within the specified household."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Required. Household identifier.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Required. Identifier of the device to be moved.",
                        },
                        "zone_id": {
                            "type": "string",
                            "description": "Required. Zone identifier where the device will be placed.",
                        },
                    },
                    "required": ["home_id", "device_id", "zone_id"],
                },
            },
        }
