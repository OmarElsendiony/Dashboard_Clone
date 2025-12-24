import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateDeviceLocation(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], device_id: str, room_id: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        
        devices = data.get("devices", {})
        if device_id:
            device = devices.get(device_id)
        else:
            return json.dumps({"success": False, "error": "No device specified"})
        if not device:
            return json.dumps({"success": False, "error": "Device not found"})

        # verify the room_id exists in data
        rooms = data.get("rooms", {})
        if room_id not in rooms:
            return json.dumps({"success": False, "error": "Room not found"})

        # Update the device location
        updated_device = (
            {**device, "room_id": room_id, "updated_at": "2025-12-19T23:59:00"}
            if room_id
            else device
        )
        devices[device_id] = updated_device
        data["devices"] = devices
        
        return json.dumps({"success": True, "device": updated_device})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_device_location",
                "description": "Update the location of a device.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to be updated.",
                        },
                        "room_id": {
                            "type": "string",
                            "description": "The new room ID for the device.",
                        },
                    },
                    "required": ["device_id", "room_id"],
                },
            },
        }
