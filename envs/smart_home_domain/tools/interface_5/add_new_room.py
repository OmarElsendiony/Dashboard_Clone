import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddNewRoom(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        room_name: str,
        room_type: str,
    ) -> str:
        """
        Create a new room in a home.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

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

        if not isinstance(room_name, str) or not room_name.strip():
            return json.dumps({"success": False, "error": "room_name must be provided"})
        room_name = room_name.strip()

        if not isinstance(room_type, str) or not room_type.strip():
            return json.dumps({"success": False, "error": "room_type must be provided"})
        room_type = room_type.strip().lower()

        allowed_types = {"bedroom", "kitchen", "lounge", "bathroom", "living_room", "dining_room", "garage", "hallway", "storage", "office", "custom"}
        if room_type not in allowed_types:
            return json.dumps({"success": False, "error": f"room_type must be one of {', '.join(allowed_types)}"})

        for room in rooms.values():
            if room.get("home_id") == home_id and room.get("room_name", "").strip().lower() == room_name.lower():
                return json.dumps({"success": False, "error": f"Room '{room_name}' already exists in this home"})

        room_id = generate_id(rooms)
        timestamp = "2025-12-19T23:59:00"

        record = {
            "room_id": room_id,
            "home_id": home_id,
            "room_name": room_name,
            "room_type": room_type,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        rooms[room_id] = record

        return json.dumps({"success": True, "room": record})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_room",
                "description": "Add a new room to a home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "room_name": {
                            "type": "string",
                            "description": "Name of the room.",
                        },
                        "room_type": {
                            "type": "string",
                            "description": "Type of room; allowed values: bedroom, kitchen, lounge, bathroom, living_room, dining_room, garage, hallway, storage, office, custom.",
                        },
                    },
                    "required": ["home_name", "room_name", "room_type"],
                },
            },
        }

