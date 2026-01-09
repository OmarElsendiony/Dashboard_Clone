import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class EnableDevice(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], device_id: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        # Implement your tool logic here
        devices = data.get("devices", {})
        timestamp = "2025-12-19T23:59:00"
        if device_id:
            device = devices.get(device_id)
        else:
            return json.dumps({"success": False, "error": "No device specified"})
        if not device:
            return json.dumps({"success": False, "error": "device not found"})
        # Update the enabled status of the device
        devices[device_id] = {**device, "status": "online", "updated_at": timestamp}
        data["devices"] = devices
        return json.dumps({"success": True, "device": devices[device_id]})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "enable_device",
                "description": "Update the status of a device to online.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        # Define your parameters here
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to be enabled.",
                        }
                    },
                    "required": ["device_id"],
                },
            },
        }
