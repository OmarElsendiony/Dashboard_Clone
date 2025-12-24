import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetRooms(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: Optional[str] = None,
        room_id: Optional[str] = None,
        room_name: Optional[str] = None,
        room_type: Optional[str] = None
    ) -> str:
        """
        Get rooms with optional filters.
        
        Args:
            data: The data dictionary containing all smart home data.
            home_id: Filter by home ID (optional).
            room_id: Filter by specific room ID (optional).
            room_name: Filter by room name (optional).
            room_type: Filter by room type (optional).
            
        Returns:
            JSON string containing list of matching rooms.
        """
        rooms = data.get("rooms", {})
        results = []
        
        for r_id, room in rooms.items():
            # Filter by room_id
            if room_id is not None and str(room.get("room_id")) != str(room_id):
                continue
            
            # Filter by home_id
            if home_id is not None and str(room.get("home_id")) != str(home_id):
                continue
            
            # Filter by room_name
            if room_name is not None and room.get("room_name") != room_name:
                continue
            
            # Filter by room_type
            if room_type is not None and room.get("room_type") != room_type:
                continue
            
            # Return full room record
            record = {
                "room_id": room.get("room_id"),
                "home_id": room.get("home_id"),
                "room_name": room.get("room_name"),
                "room_type": room.get("room_type"),
                "created_at": room.get("created_at"),
                "updated_at": room.get("updated_at"),
                "room_description": room.get("room_description")
            }
            results.append(record)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "rooms": results
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_rooms",
                "description": "Get rooms with optional filters. Returns room details including room_id, home_id, room_name, room_type, created_at, updated_at, and room_description.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Filter rooms by home ID (optional)."
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Filter by specific room ID (optional)."
                        },
                        "room_name": {
                            "type": "string",
                            "description": "Filter by room name (optional)."
                        },
                        "room_type": {
                            "type": "string",
                            "description": "Filter by room type (optional). Examples: 'bedroom', 'living_room', 'kitchen', 'bathroom', 'hallway', 'custom'."
                        }
                    },
                    "required": []
                }
            }
        }
