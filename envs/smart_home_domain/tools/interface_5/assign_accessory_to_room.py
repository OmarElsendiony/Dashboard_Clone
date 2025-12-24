import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AssignAccessoryToRoom(Tool):
    """
    Assign a device to a room.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        accessory_id: str,
        room_id: str,
    ) -> str:
        """
        Assign an accessory to a specific room within a home.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        devices = data.get("devices")
        rooms = data.get("rooms")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(devices, dict):
            return json.dumps({"success": False, "error": "devices store missing"})
        if not isinstance(rooms, dict):
            return json.dumps({"success": False, "error": "rooms store missing"})

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

        if not isinstance(accessory_id, str) or not accessory_id.strip():
            return json.dumps({"success": False, "error": "accessory_id must be provided"})
        accessory_id = accessory_id.strip()

        if accessory_id not in devices:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' not found"})

        if not isinstance(room_id, str) or not room_id.strip():
            return json.dumps({"success": False, "error": "room_id must be provided"})
        room_id = room_id.strip()

        if room_id not in rooms:
            return json.dumps({"success": False, "error": f"Room '{room_id}' not found"})

        device = devices[accessory_id]
        room = rooms[room_id]

        if room.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Room '{room_id}' does not belong to home '{home_name}'"})
        if device.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' does not belong to home '{home_name}'"})

        device["room_id"] = room_id
        device["updated_at"] = "2025-12-19T23:59:00"

        return json.dumps({
            "success": True,
            "accessory": {
                "accessory_id": device.get("device_id") or accessory_id,
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
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_accessory_to_room",
                "description": "Assign an accessory to a room within a home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "accessory_id": {
                            "type": "string",
                            "description": "Identifier of the accessory.",
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Identifier of the room.",
                        },
                    },
                    "required": ["home_name", "accessory_id", "room_id"],
                },
            },
        }

