import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateDeviceName(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], device_id: str, new_name: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        
        devices = data.get("devices", {})
        if device_id:
            device = devices.get(device_id)
        else:
            return json.dumps({"success": False, "error": "No device specified"})
        if not device:
            return json.dumps({"success": False, "error": "Device not found"})
        # Update the device name
        updated_device = (
            {**device, "device_name": new_name, "updated_at": "2025-12-19T23:59:00"}
            if new_name
            else device
        )
        devices[device_id] = updated_device
        data["devices"] = devices
        
        return json.dumps({"success": True, "device": updated_device})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_device_name",
                "description": "Update the name of a device.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to be updated.",
                        },
                        "new_name": {
                            "type": "string",
                            "description": "The new name for the device.",
                        },
                    },
                    "required": ["device_id", "new_name"],
                },
            },
        }
