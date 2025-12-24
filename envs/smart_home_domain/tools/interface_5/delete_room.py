import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class DeleteRoom(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        room_id: str,
    ) -> str:
        """
        Delete a room and unassign devices from it. Room must belong to the specified home.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        rooms = data.get("rooms")
        devices = data.get("devices")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
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

        if not isinstance(room_id, str) or not room_id.strip():
            return json.dumps({"success": False, "error": "room_id must be provided"})
        room_id = room_id.strip()

        if room_id not in rooms:
            return json.dumps({"success": False, "error": f"Room '{room_id}' not found"})
        
        room = rooms[room_id]
        
        # Verify room belongs to the specified home
        if room.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Room '{room_id}' does not belong to home '{home_name}'"})

        deleted_room = rooms.pop(room_id)

        if isinstance(devices, dict):
            for device in devices.values():
                if device.get("room_id") == room_id:
                    device["room_id"] = None

        return json.dumps({"success": True, "deleted_room": deleted_room})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_room",
                "description": "Delete a room from a home. Room must belong to the specified home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Identifier of the room to delete.",
                        },
                    },
                    "required": ["home_name", "room_id"],
                },
            },
        }

