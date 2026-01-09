import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateDeviceLocation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        device_id: str,
        room_id: Optional[str] = None,
        room_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        # Implement your tool logic here
        devices = data.get("devices", {})

        if device_id:
            device = devices.get(device_id)
        else:
            return json.dumps({"success": False, "error": "No device specified"})
        if not device:
            return json.dumps({"success": False, "error": "Device not found"})
        if room_name and not room_id:
            # Find room_id by room_name
            rooms = data.get("rooms", {})
            for r in rooms.values():
                if r.get("room_name") == room_name and device.get("home_id") == r.get(
                    "home_id"
                ):
                    room_id = r.get("room_id")
                    break
            if not room_id:
                return json.dumps({"success": False, "error": "Room not found"})

        # verify the room_id exists in data
        rooms = data.get("rooms", {})
        room = rooms.get(room_id)

        if not room:
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
                        # Define your parameters here
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to be updated.",
                        },
                        "room_id": {
                            "type": "string",
                            "description": "The new room ID for the device.",
                        },
                        "room_name": {
                            "type": "string",
                            "description": "The new room name for the device.",
                        },
                    },
                    "required": ["device_id"],
                },
            },
        }
