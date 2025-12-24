import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class EditRoomInformation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        room_id: str,
        new_room_name: str,
    ) -> str:
        """
        Rename a room within a home.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        rooms = data.get("rooms")

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
        if room.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Room '{room_id}' does not belong to home '{home_name}'"})

        if not isinstance(new_room_name, str) or not new_room_name.strip():
            return json.dumps({"success": False, "error": "new_room_name must be provided"})
        new_name = new_room_name.strip()

        # Duplicate detection within the home
        for rid, r in rooms.items():
            if rid != room_id and r.get("home_id") == home_id and r.get("room_name", "").strip().lower() == new_name.lower():
                return json.dumps({"success": False, "error": f"Room '{new_name}' already exists in this home"})

        room["room_name"] = new_name

        room["updated_at"] = "2025-12-19T23:59:00"

        return json.dumps({"success": True, "room": room})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "edit_room_information",
                "description": "Rename an existing room within a home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Identifier of the room to rename.",
                        },
                        "new_room_name": {
                            "type": "string",
                            "description": "New room name.",
                        },
                    },
                    "required": ["home_name", "room_id", "new_room_name"],
                },
            },
        }

