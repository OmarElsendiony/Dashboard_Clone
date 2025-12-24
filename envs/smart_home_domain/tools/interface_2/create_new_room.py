import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateNewRoom(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        room_name: str,
        room_type: str,
        room_description: Optional[str] = None
    ) -> str:
        """
        Create a new room in a home.
        
        Args:
            data: The data dictionary containing all smart home data.
            home_id: The home ID where the room will be created (required).
            room_name: The name of the room (required).
            room_type: The type of room (required).
            room_description: Custom description for the room (optional, auto-generated if not provided).
            
        Returns:
            JSON string containing the success status and the newly created room.
        """
        # Validate room_type
        valid_room_types = [
            "bathroom", "bedroom", "custom", "dining_room", "garage",
            "hallway", "kitchen", "living_room", "lounge", "office", "storage"
        ]
        if room_type not in valid_room_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid room_type '{room_type}'. Valid types are: {', '.join(valid_room_types)}"
            })
        
        rooms = data.setdefault("rooms", {})
        homes = data.get("homes", {})
        
        # Validate that the home exists
        if str(home_id) not in homes:
            return json.dumps({
                "success": False,
                "error": f"Home ID {home_id} not found"
            })
        
        # Generate new room ID
        if rooms:
            max_id = max([int(k) for k in rooms.keys()])
            new_room_id = str(max_id + 1)
        else:
            new_room_id = "1"
        
        # Get current timestamp
        current_timestamp = "2025-12-19T23:59:00"
        
        # Use provided description or generate one based on room type
        if room_description is None:
            room_descriptions = {
                "bedroom": "Private sleeping quarters with comfort and rest optimization",
                "living_room": "Main gathering space with lighting and entertainment systems",
                "kitchen": "Food preparation and dining area with appliance control",
                "bathroom": "Personal hygiene space with water and climate management",
                "hallway": "Transitional passage connecting different areas",
                "garage": "Vehicle storage and workshop area with door automation",
                "office": "Workspace with productivity and focus optimization",
                "dining_room": "Formal dining area with ambiance control",
                "lounge": "Relaxation and leisure space with entertainment control",
                "storage": "Storage area for organizing items and equipment",
                "custom": "User-defined room for custom automation"
            }
            room_description = room_descriptions.get(room_type, "Custom room for home automation")
        
        # Create new room record
        new_room = {
            "room_id": new_room_id,
            "home_id": str(home_id),
            "room_name": room_name,
            "room_type": room_type,
            "created_at": current_timestamp,
            "updated_at": current_timestamp,
            "room_description": room_description
        }
        
        # Add room to the rooms dictionary
        rooms[new_room_id] = new_room
        
        return json.dumps({
            "success": True,
            **new_room
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_room",
                "description": "Create a new room in a home. Automatically generates room_id, timestamps, and a description based on room_type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The home ID where the room will be created (required)."
                        },
                        "room_name": {
                            "type": "string",
                            "description": "The name of the room (required)."
                        },
                        "room_type": {
                            "type": "string",
                            "enum": ["bathroom", "bedroom", "custom", "dining_room", "garage", "hallway", "kitchen", "living_room", "lounge", "office", "storage"],
                            "description": "The type of room (required). Must be one of the predefined room types."
                        },
                        "room_description": {
                            "type": "string",
                            "description": "Custom description for the room (optional). If not provided, a description will be auto-generated based on room_type."
                        }
                    },
                    "required": ["home_id", "room_name", "room_type"]
                }
            }
        }
