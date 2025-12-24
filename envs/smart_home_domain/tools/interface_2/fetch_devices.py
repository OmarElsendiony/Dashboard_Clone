import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class FetchDevices(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        device_ids: Optional[List[str]] = None,
        device_names: Optional[List[str]] = None,
        room_id: Optional[str] = None,
        device_type: Optional[str] = None,
        status: Optional[str] = None,
        support_automation: Optional[bool] = None,
        serial_number: Optional[str] = None
    ) -> str:
        """
        Fetch devices from the smart home system with optional filters.
        
        Args:
            data: The data dictionary containing all smart home data.
            home_id: Filter by home ID (required).
            device_ids: Filter by a list of device IDs.
            device_names: Filter by a list of device names.
            room_id: Filter by room ID.
            device_type: Filter by device type (e.g., 'temperature_sensor', 'power_outlet', 'door_lock', etc.).
            status: Filter by status ('online' or 'offline').
            support_automation: Filter by automation support (True or False).
            serial_number: Filter by serial number.
            
        Returns:
            JSON string containing the list of matching devices.
        """
        devices = data.get("devices", {})
        results = []

        for device_id, device in devices.items():
            # Filter by device_ids list
            if device_ids is not None and str(device.get("device_id")) not in device_ids:
                continue
            
            # Filter by device_names list
            if device_names is not None and device.get("device_name") not in device_names:
                continue
            
            # Filter by home_id
            if str(device.get("home_id")) != str(home_id):
                continue
            
            # Filter by room_id
            if room_id is not None and str(device.get("room_id")) != str(room_id):
                continue
            
            # Filter by device_type
            if device_type is not None and device.get("device_type") != device_type:
                continue
            
            # Filter by status
            if status is not None and device.get("status") != status:
                continue
            
            # Filter by support_automation
            if support_automation is not None and device.get("support_automation") != support_automation:
                continue
            
            # Filter by serial_number
            if serial_number is not None and device.get("serial_number") != serial_number:
                continue

            # Return full device record as specified in the database
            record = {
                "device_id": device.get("device_id"),
                "home_id": device.get("home_id"),
                "room_id": device.get("room_id"),
                "device_name": device.get("device_name"),
                "device_type": device.get("device_type"),
                "serial_number": device.get("serial_number"),
                "status": device.get("status"),
                "support_automation": device.get("support_automation"),
                "installed_at": device.get("installed_at"),
                "last_seen": device.get("last_seen"),
                "created_at": device.get("created_at"),
                "updated_at": device.get("updated_at")
            }
            results.append(record)

        return json.dumps({
            "success": True,
            "count": len(results),
            "devices": results
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_devices",
                "description": "Fetch devices from a specific home in the smart home system. Requires home_id. Additional optional filters available for device_ids, device_names, room_id, device_type, status, support_automation, and serial_number. Returns device details including device_id, home_id, room_id, device_name, device_type, serial_number, status, support_automation, installed_at, last_seen, created_at, and updated_at.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Filter devices by home ID (required)."
                        },
                        "device_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter devices by a list of device IDs."
                        },
                        "device_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter devices by a list of device names."
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Filter devices by room ID."
                        },
                        "device_type": {
                            "type": "string",
                            "description": "Filter devices by device type (e.g., 'temperature_sensor', 'power_outlet', 'door_lock', 'motion_sensor', 'air_conditioner', 'camera', 'bulb', 'water_leak_sensor', 'humidity_sensor', 'door_sensor')."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["online", "offline"],
                            "description": "Filter devices by status."
                        },
                        "support_automation": {
                            "type": "boolean",
                            "description": "Filter devices by automation support capability."
                        },
                        "serial_number": {
                            "type": "string",
                            "description": "Filter devices by serial number."
                        }
                    },
                    "required": ["home_id"]
                }
            }
        }
