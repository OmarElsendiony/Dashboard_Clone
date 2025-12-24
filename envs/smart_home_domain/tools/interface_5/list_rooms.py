import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListRooms(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        home_id: Optional[str] = None,
        room_type: Optional[str] = None,
    ) -> str:
        """
        List rooms in a home, optionally filtered by room type.
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
        if not isinstance(devices, dict):
            return json.dumps({"success": False, "error": "devices store missing"})

        resolved_home_id = None
        resolved_home_name = None

        # Priority to home_id if provided
        if home_id is not None:
            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps({"success": False, "error": "home_id must be a non-empty string"})
            home_id_val = home_id.strip()
            if home_id_val not in homes:
                return json.dumps({"success": False, "error": f"Home '{home_id_val}' not found"})
            resolved_home_id = home_id_val
            resolved_home_name = homes[home_id_val].get("home_name")
        else:
            if not isinstance(home_name, str) or not home_name.strip():
                return json.dumps({"success": False, "error": "home_name must be a non-empty string"})
            home_name_val = home_name.strip()

            # Find home by name
            for hid, home in homes.items():
                if home.get("home_name", "").strip().lower() == home_name_val.lower():
                    resolved_home_id = hid
                    resolved_home_name = home.get("home_name")
                    break

            if not resolved_home_id:
                return json.dumps({"success": False, "error": f"Home '{home_name_val}' not found"})

        type_filter = None
        if room_type:
            if not isinstance(room_type, str):
                return json.dumps({"success": False, "error": "room_type must be a string"})
            type_filter = room_type.strip().lower()
            allowed_types = {"bedroom", "kitchen", "lounge", "bathroom", "living_room", "dining_room", "garage", "hallway", "storage", "office", "custom"}
            if type_filter not in allowed_types:
                return json.dumps({"success": False, "error": f"room_type must be one of {', '.join(allowed_types)}"})

        result_rooms = []
        for room_id, room in rooms.items():
            if room.get("home_id") == resolved_home_id:
                if type_filter and room.get("room_type") != type_filter:
                    continue
                # Attach all accessories assigned to this room (SOP terminology)
                assigned_accessories = []
                for did, dev in devices.items():
                    if dev.get("home_id") != resolved_home_id:
                        continue
                    if dev.get("room_id") != (room.get("room_id") or room_id):
                        continue
                    assigned_accessories.append({
                        "accessory_id": dev.get("device_id") or did,
                        "accessory_name": dev.get("device_name"),
                        "accessory_type": dev.get("device_type"),
                        "status": dev.get("status"),
                        "serial_number": dev.get("serial_number"),
                        "support_automation": dev.get("support_automation"),
                        "installed_at": dev.get("installed_at"),
                        "last_seen": dev.get("last_seen"),
                        "created_at": dev.get("created_at"),
                        "updated_at": dev.get("updated_at"),
                    })
                result_rooms.append({
                    "home_name": resolved_home_name,
                    "room_id": room.get("room_id") or room_id,
                    "room_name": room.get("room_name"),
                    "room_type": room.get("room_type"),
                    "accessories": assigned_accessories,
                    "created_at": room.get("created_at"),
                    "updated_at": room.get("updated_at"),
                })

        return json.dumps({"success": True, "rooms": result_rooms})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_rooms",
                "description": "List all rooms in a home, optionally filtered by room type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Optional identifier of the home. If both home_name and home_id are provided, home_id takes priority.",
                        },
                        "room_type": {
                            "type": "string",
                            "description": "Optional room type filter; allowed values: bedroom, kitchen, lounge, bathroom, living_room, dining_room, garage, hallway, storage, office, custom.",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }

