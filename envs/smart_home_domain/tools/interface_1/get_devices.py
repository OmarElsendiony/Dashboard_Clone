import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetDevices(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        devices = data.get("devices", {})
        homes = data.get("homes", {})
        # Find home_id if home_name is provided
        if home_name and not home_id:
            for h_id, home in homes.items():
                if home.get("home_name").strip().lower() == home_name.strip().lower():
                    home_id = h_id
                    break
        if not home_id:
            return json.dumps(
                {"success": False, "error": "Home ID or name must be provided"}
            )
        target_devices = [
            device for device in devices.values() if device.get("home_id") == home_id
        ]
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                target_devices = [
                    device for device in target_devices if device.get(key) == value
                ]

        return json.dumps({"success": True, "devices": target_devices})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_devices",
                "description": "Retrieves a list of devices in a specific home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        # Define your parameters here
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home.",
                        },
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home.",
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filters to apply when retrieving devices. Including [device_type, status, device_name, room_id support_automation] ",
                        },
                    },
                    "required": [],
                },
            },
        }
