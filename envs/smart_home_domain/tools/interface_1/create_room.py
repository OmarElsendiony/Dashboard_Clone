import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateRoom(Tool):
    """
    Create a new room in a home.
    - Requires home_id, room_name, and room_type.
    - Validates that home exists.
    - Auto-generates room_id, created_at, and updated_at.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        room_name: str,
        room_type: str
    ) -> str:
        """
        Create a new room in a home.
        
        Args:
            data: The data dictionary containing homes and rooms
            home_id: The ID of the home where the room will be created
            room_name: The name of the room
            room_type: The type of the room
            
        Returns:
            JSON string with success status and created room information
        """
        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid homes container: expected dict at data['homes']"
            })

        rooms_dict = data.get("rooms", {})
        if not isinstance(rooms_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid rooms container: expected dict at data['rooms']"
            })

        # Validate required fields
        if home_id is None:
            return json.dumps({"success": False, "error": "home_id is required"})

        if not room_name or not room_name.strip():
            return json.dumps({
                "success": False,
                "error": "room_name is required and cannot be empty"
            })

        if room_type is None:
            return json.dumps({"success": False, "error": "room_type is required"})

        # Convert IDs to strings for consistent comparison
        home_id_str = str(home_id)
        room_name_str = str(room_name).strip()
        room_type_str = str(room_type)

        # Validate home exists
        if home_id_str not in homes_dict:
            return json.dumps({
                "success": False,
                "error": f"Home not found: '{home_id_str}'"
            })

        # Validate room_type is valid
        valid_room_types = [
            "kitchen", "office", "garage", "custom", "storage", 
            "hallway", "living_room", "lounge", "dining_room", 
            "bathroom", "bedroom"
        ]
        if room_type_str not in valid_room_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid room_type: '{room_type_str}'. Must be one of {valid_room_types}"
            })

        # Generate new room ID
        def generate_room_id(rooms: Dict[str, Any]) -> str:
            if not rooms:
                return "1"
            try:
                max_id = max(int(k) for k in rooms.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                # If no numeric keys, start from 1
                return "1"

        new_room_id = generate_room_id(rooms_dict)

        current_time = "2025-12-19T23:59:00"

        # Create new room
        new_room = {
            "room_id": new_room_id,
            "home_id": home_id_str,
            "room_name": room_name_str,
            "room_type": room_type_str,
            "created_at": current_time,
            "updated_at": current_time
        }

        # Add room to data (modify in place)
        rooms_dict[new_room_id] = new_room

        return json.dumps({
            "success": True,
            "room": new_room,
            "message": f"Room '{room_name_str}' created successfully in home '{home_id_str}'"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "create_room",
                "description": (
                    "Create a new room in a home. "
                    "Requires home_id, room_name, and room_type. "
                    "Validates that home exists. "
                    "Auto-generates room_id, created_at, and updated_at. "
                    "Valid room types: kitchen, office, garage, custom, storage, hallway, living_room, lounge, dining_room, bathroom, bedroom."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home where the room will be created (required)."
                        },
                        "room_name": {
                            "type": "string",
                            "description": "The name of the room (required, cannot be empty)."
                        },
                        "room_type": {
                            "type": "string",
                            "description": "The type of the room (required). Valid values: kitchen, office, garage, custom, storage, hallway, living_room, lounge, dining_room, bathroom, bedroom."
                        }
                    },
                    "required": ["home_id", "room_name", "room_type"],
                },
            },
        }

