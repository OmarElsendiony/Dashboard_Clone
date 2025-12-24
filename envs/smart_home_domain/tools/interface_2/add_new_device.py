import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddNewDevice(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        device_name: str,
        device_type: str,
        room_id: Optional[str] = None,
        serial_number: Optional[str] = None,
        status: Optional[str] = None,
        support_automation: Optional[bool] = None,
        installed_at: Optional[str] = None
    ) -> str:
        """
        Add a new device to the smart home system.
        
        Args:
            data: The data dictionary containing all smart home data.
            home_id: The home ID where the device will be added (required).
            device_name: The name of the device (required).
            device_type: The type of device (required).
            room_id: The room ID where the device will be installed (optional).
            serial_number: The device serial number (optional, auto-generated if not provided).
            status: The device status (optional, defaults to 'online').
            support_automation: Whether the device supports automation (optional, defaults to False).
            installed_at: Installation timestamp (optional, defaults to current timestamp).
            
        Returns:
            JSON string containing the success status and the new device_id.
        """
        # Validate device_type
        valid_device_types = [
            "air_conditioner", "bulb", "camera", "door_lock", "door_sensor",
            "humidity_sensor", "motion_sensor", "power_outlet",
            "temperature_sensor", "water_leak_sensor"
        ]
        if device_type not in valid_device_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid device_type '{device_type}'. Valid types are: {', '.join(valid_device_types)}"
            })
        
        # Validate room_id if provided
        if room_id is not None:
            rooms = data.get("rooms", {})
            if str(room_id) not in rooms:
                return json.dumps({
                    "success": False,
                    "error": f"Room with room_id '{room_id}' does not exist"
                })
        
        devices = data.setdefault("devices", {})
        
        # Generate new device ID
        if devices:
            max_id = max([int(k) for k in devices.keys()])
            new_device_id = str(max_id + 1)
        else:
            new_device_id = "1"
        
        # Get current timestamp
        current_timestamp = "2025-12-19T23:59:00"
        
        # Set defaults for optional fields
        if serial_number is None:
            serial_number = f"SN-{new_device_id.zfill(8)}"
        
        if status is None:
            status = "online"
        
        if support_automation is None:
            support_automation = False
        
        if installed_at is None:
            installed_at = current_timestamp
        
        # Create new device record with all required fields
        new_device = {
            "device_id": new_device_id,
            "home_id": str(home_id),
            "room_id": str(room_id) if room_id is not None else None,
            "device_name": device_name,
            "device_type": device_type,
            "serial_number": serial_number,
            "status": status,
            "support_automation": support_automation,
            "installed_at": installed_at,
            "last_seen": current_timestamp if status == "online" else None,
            "created_at": current_timestamp,
            "updated_at": current_timestamp
        }
        
        # Add device to the devices dictionary
        devices[new_device_id] = new_device
        
        return json.dumps({
            "success": True,
            "device_id": new_device,
            "message": f"Device '{device_name}' added successfully"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_device",
                "description": "Add a new device to the smart home system. Returns the newly created device_id. Serial number is auto-generated if not provided. Status defaults to 'online' and support_automation defaults to False if not specified.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The home ID where the device will be added (required)."
                        },
                        "device_name": {
                            "type": "string",
                            "description": "The name of the device (required)."
                        },
                        "device_type": {
                            "type": "string",
                            "enum": ["air_conditioner", "bulb", "camera", "door_lock", "door_sensor", "humidity_sensor", "motion_sensor", "power_outlet", "temperature_sensor", "water_leak_sensor"],
                            "description": "The type of device (required). Must be one of the predefined device types."
                        },
                        "room_id": {
                            "type": "string",
                            "description": "The room ID where the device will be installed (optional)."
                        },
                        "serial_number": {
                            "type": "string",
                            "description": "The device serial number (optional, auto-generated if not provided)."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["online", "offline"],
                            "description": "The device status (optional, defaults to 'online')."
                        },
                        "support_automation": {
                            "type": "boolean",
                            "description": "Whether the device supports automation (optional, defaults to False)."
                        },
                        "installed_at": {
                            "type": "string",
                            "description": "Installation timestamp in ISO format (optional, defaults to current timestamp)."
                        }
                    },
                    "required": ["home_id", "device_name", "device_type"]
                }
            }
        }
