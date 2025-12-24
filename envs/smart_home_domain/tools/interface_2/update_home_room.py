import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateHomeRoom(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        room_id: Optional[str] = None,
        room_name: Optional[str] = None,
        room_type: Optional[str] = None,
        room_description: Optional[str] = None
    ) -> str:
        """
        Update an existing room in the smart home system.
        
        Args:
            data: The data dictionary containing all smart home data.
            home_id: The home ID where the room is located (required).
            room_id: The room ID to update (optional, used to identify the room).
            room_name: Updated room name (optional, can also be used to identify the room if room_id is not provided).
            room_type: Updated room type (optional).
            room_description: Updated room description (optional).
            
        Returns:
            JSON string containing the success status and updated room information.
        """
        rooms = data.get("rooms", {})
        homes = data.get("homes", {})
        
        timestamp = "2025-12-19T23:59:00"
        
        # Validate that the home exists
        if str(home_id) not in homes:
            return json.dumps({
                "success": False,
                "error": f"Home ID {home_id} not found"
            })
        
        # Find the room to update
        target_room = None
        
        if room_id is not None:
            # Find by room_id
            target_room = rooms.get(room_id)
            if target_room and str(target_room.get("home_id")) == str(home_id):
                pass
            elif target_room:
                return json.dumps({
                    "success": False,
                    "error": f"Room ID {room_id} does not belong to Home ID {home_id}"
                })
        
        if target_room is None and room_name is not None:
            # Find by home_id + room_name (existing room_name)
            for room in rooms.values():
                if str(room.get("home_id")) == str(home_id) and room.get("room_name") == room_name:
                    target_room = room
                    break
        
        if target_room is None:
            return json.dumps({
                "success": False,
                "error": f"Room not found in Home ID {home_id}. Provide either room_id or an existing room_name to identify the room."
            })
        
        # Update room fields (only if new values are provided)
        if room_name is not None:
            target_room["room_name"] = room_name
        if room_type is not None:
            target_room["room_type"] = room_type
        if room_description is not None:
            target_room["room_description"] = room_description
        
        target_room["updated_at"] = timestamp
        
        # Return the complete updated room with success status
        result = {
            "success": True,
            **dict(target_room)
        }
        
        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_home_room",
                "description": "Update an existing room in the smart home system. Requires home_id. The room can be identified by either room_id or room_name (existing name). Only provided fields will be updated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The home ID where the room is located (required)."
                        },
                        "room_id": {
                            "type": "string",
                            "description": "The room ID to update (optional, used to identify the room)."
                        },
                        "room_name": {
                            "type": "string",
                            "description": "Room name - used to identify the room if room_id is not provided, or to update the room name (optional)."
                        },
                        "room_type": {
                            "type": "string",
                            "description": "Updated room type (optional). Examples: 'bedroom', 'living_room', 'kitchen', 'bathroom', 'hallway', 'garage', 'office', 'dining_room', 'custom'."
                        },
                        "room_description": {
                            "type": "string",
                            "description": "Updated room description (optional)."
                        }
                    },
                    "required": ["home_id"]
                }
            }
        }
