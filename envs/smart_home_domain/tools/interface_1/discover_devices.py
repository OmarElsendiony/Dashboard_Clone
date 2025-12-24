import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class DiscoverDevices(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str
    ) -> str:
        """
        Discover all devices in a specific home that are yet to be assigned to a room.
        
        Args:
            data: The data dictionary containing devices and homes information
            home_id: The ID of the home to discover devices for
            
        Returns:
            JSON string with success status and list of unassigned devices
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        # Validate home_id is provided
        home_id = str(home_id)
        
        # Get homes and devices data
        homes = data.get("homes", {})
        devices = data.get("devices", {})
        
        # Check if home exists
        if home_id not in homes:
            return json.dumps({
                "success": False,
                "error": f"Home not found: '{home_id}'"
            })
        
        # Filter devices by home_id and only include devices not yet assigned to a room
        discovered_devices = []
        for device_id, device_data in devices.items():
            device_room_id = device_data.get("room_id")
            # Only include devices that belong to the home and are not assigned to any room
            if str(device_data.get("home_id")) == home_id and (device_room_id is None or device_room_id == ""):
                discovered_devices.append({
                    **device_data,
                    "device_id": device_id
                })
        
        # Sort by device_id for consistent ordering
        discovered_devices.sort(key=lambda x: int(x["device_id"]))
        
        return json.dumps({
            "success": True,
            "home_id": home_id,
            "count": len(discovered_devices),
            "devices": discovered_devices
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "discover_devices",
                "description": "Discover all devices in a specific home that are yet to be assigned to a room. Returns only devices that have not been assigned to any room (room_id is null).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home to discover devices for"
                        }
                    },
                    "required": ["home_id"],
                },
            },
        }

