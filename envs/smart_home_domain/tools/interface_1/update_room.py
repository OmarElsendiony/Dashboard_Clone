import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateRoom(Tool):
    """
    Update an existing room's properties.
    - Requires home_name, room_name, and updates dict.
    - Validates that home and room exist.
    - Updates the 'updated_at' timestamp automatically.
    - Validates room_type if being updated.
    - Does not allow updating room_id, home_id, or created_at.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        room_name: str,
        updates: Dict[str, Any]
    ) -> str:
        """
        Update an existing room's properties.
        
        Args:
            data: The data dictionary containing homes and rooms
            home_name: The name of the home containing the room
            room_name: The current name of the room to update
            updates: Dictionary of fields to update (room_name, room_type)
            
        Returns:
            JSON string with success status and updated room information
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
        if home_name is None or not home_name.strip():
            return json.dumps({
                "success": False,
                "error": "home_name is required and cannot be empty"
            })

        if room_name is None or not room_name.strip():
            return json.dumps({
                "success": False,
                "error": "room_name is required and cannot be empty"
            })

        if not isinstance(updates, dict):
            return json.dumps({
                "success": False,
                "error": "updates must be a dictionary"
            })

        if not updates:
            return json.dumps({
                "success": False,
                "error": "updates dictionary cannot be empty"
            })

        # Convert to strings for consistent comparison
        home_name_str = str(home_name).strip()
        room_name_str = str(room_name).strip()

        # Find home by home_name
        home_id = None
        for hid, home in homes_dict.items():
            if isinstance(home, dict) and home.get("home_name") == home_name_str:
                home_id = hid
                break

        if home_id is None:
            return json.dumps({
                "success": False,
                "error": f"Home not found with name: '{home_name_str}'"
            })

        # Find room by room_name within the specified home
        room_id = None
        room_data = None
        for rid, room in rooms_dict.items():
            if isinstance(room, dict) and room.get("room_name") == room_name_str and str(room.get("home_id")) == home_id:
                room_id = rid
                room_data = room
                break

        if room_id is None:
            return json.dumps({
                "success": False,
                "error": f"Room not found with name '{room_name_str}' in home '{home_name_str}'"
            })

        # Validate that protected fields are not in updates
        protected_fields = ["room_id", "home_id", "created_at"]
        for field in protected_fields:
            if field in updates:
                return json.dumps({
                    "success": False,
                    "error": f"Cannot update protected field: '{field}'"
                })

        # Valid room types
        valid_room_types = [
            "kitchen", "office", "garage", "custom", "storage", 
            "hallway", "living_room", "lounge", "dining_room", 
            "bathroom", "bedroom"
        ]

        # Validate room_type if being updated
        if "room_type" in updates:
            new_room_type = str(updates["room_type"])
            if new_room_type not in valid_room_types:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid room_type: '{new_room_type}'. Must be one of {valid_room_types}"
                })

        # Check if new room_name already exists in the same home
        if "room_name" in updates:
            new_room_name = str(updates["room_name"]).strip()
            if not new_room_name:
                return json.dumps({
                    "success": False,
                    "error": "room_name cannot be empty"
                })
            
            # Check for duplicate room name in same home (excluding current room)
            for rid, room in rooms_dict.items():
                if rid != room_id and isinstance(room, dict) and str(room.get("home_id")) == home_id:
                    if room.get("room_name") == new_room_name:
                        return json.dumps({
                            "success": False,
                            "error": f"A room with name '{new_room_name}' already exists in home '{home_name_str}'"
                        })

        # Apply updates
        current_time = "2025-12-19T23:59:00"
        
        for key, value in updates.items():
            if key in ["room_name", "room_type"]:
                room_data[key] = str(value).strip() if key == "room_name" else str(value)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid update field: '{key}'. Allowed fields: room_name, room_type"
                })

        # Always update timestamp
        room_data["updated_at"] = current_time

        return json.dumps({
            "success": True,
            "message": f"Room '{room_name_str}' in home '{home_name_str}' updated successfully",
            "room": room_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_room",
                "description": (
                    "Update an existing room's properties. "
                    "Requires home_name, room_name, and updates dictionary. "
                    "Validates that home and room exist. "
                    "Updates the 'updated_at' timestamp automatically. "
                    "Validates room_type if being updated. "
                    "Allowed update fields: room_name, room_type. "
                    "Cannot update room_id, home_id, or created_at. "
                    "Valid room types: kitchen, office, garage, custom, storage, hallway, living_room, lounge, dining_room, bathroom, bedroom."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home containing the room (required)."
                        },
                        "room_name": {
                            "type": "string",
                            "description": "The current name of the room to update (required)."
                        },
                        "updates": {
                            "type": "object",
                            "description": "Dictionary of fields to update. Allowed fields: room_name (new name), room_type (must be valid type).",
                            "additionalProperties": True
                        }
                    },
                    "required": ["home_name", "room_name", "updates"],
                },
            },
        }

