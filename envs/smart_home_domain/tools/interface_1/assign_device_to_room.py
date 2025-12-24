import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AssignDeviceToRoom(Tool):
    """
    Assign a device to a room within a home.
    - Requires home_name, device_id, and room_name.
    - Validates that home, device, and room all exist.
    - Validates that device belongs to the specified home.
    - Validates that room belongs to the specified home.
    - Updates device's room_id and updated_at timestamp.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        device_id: str,
        room_name: str
    ) -> str:
        """
        Assign a device to a room within a home.
        
        Args:
            data: The data dictionary containing homes, rooms, and devices
            home_name: The name of the home
            device_id: The ID of the device to assign
            room_name: The name of the room to assign the device to
            
        Returns:
            JSON string with success status and updated device information
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

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid devices container: expected dict at data['devices']"
            })

        # Validate required fields
        if home_name is None or not home_name.strip():
            return json.dumps({
                "success": False,
                "error": "home_name is required and cannot be empty"
            })

        if device_id is None:
            return json.dumps({"success": False, "error": "device_id is required"})

        if room_name is None or not room_name.strip():
            return json.dumps({
                "success": False,
                "error": "room_name is required and cannot be empty"
            })

        # Convert to strings for consistent comparison
        home_name_str = str(home_name).strip()
        device_id_str = str(device_id)
        room_name_str = str(room_name).strip()

        # Find home by home_name
        home_id = None
        home_data = None
        for hid, home in homes_dict.items():
            if isinstance(home, dict) and home.get("home_name") == home_name_str:
                home_id = hid
                home_data = home
                break

        if home_id is None:
            return json.dumps({
                "success": False,
                "error": f"Home not found with name: '{home_name_str}'"
            })

        # Validate device exists
        if device_id_str not in devices_dict:
            return json.dumps({
                "success": False,
                "error": f"Device not found: '{device_id_str}'"
            })

        device_data = devices_dict[device_id_str]

        # Validate device belongs to the specified home
        if str(device_data.get("home_id")) != home_id:
            return json.dumps({
                "success": False,
                "error": f"Device '{device_id_str}' does not belong to home '{home_name_str}' (home_id: '{home_id}')"
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

        # Update device's room_id and updated_at
        current_time = "2025-12-19T23:59:00"
        device_data["room_id"] = room_id
        device_data["updated_at"] = current_time

        return json.dumps({
            "success": True,
            "message": f"Device '{device_data.get('device_name')}' (ID: {device_id_str}) successfully assigned to room '{room_name_str}' (ID: {room_id}) in home '{home_name_str}'",
            "device": {
                "device_id": device_id_str,
                "device_name": device_data.get("device_name"),
                "home_id": device_data.get("home_id"),
                "room_id": room_id,
                "room_name": room_name_str,
                "updated_at": current_time
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "assign_device_to_room",
                "description": (
                    "Assign a device to a room within a home. "
                    "Requires home_name, device_id, and room_name. "
                    "Validates that home, device, and room all exist. "
                    "Validates that device belongs to the specified home and room belongs to the same home. "
                    "Updates device's room_id and updated_at timestamp."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home (required)."
                        },
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to assign (required)."
                        },
                        "room_name": {
                            "type": "string",
                            "description": "The name of the room to assign the device to (required)."
                        }
                    },
                    "required": ["home_name", "device_id", "room_name"],
                },
            },
        }

