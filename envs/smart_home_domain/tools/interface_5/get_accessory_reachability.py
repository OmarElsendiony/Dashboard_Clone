import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class GetAccessoryReachability(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        accessory_name: str,
    ) -> str:
        """
        Check accessory online/offline status.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        devices = data.get("devices")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(devices, dict):
            return json.dumps({"success": False, "error": "devices store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        for hid, home in homes.items():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                break
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        if not isinstance(accessory_name, str) or not accessory_name.strip():
            return json.dumps({"success": False, "error": "accessory_name must be provided"})
        accessory_name = accessory_name.strip()

        # Find accessory by name within the home
        matches = []
        for did, dev in devices.items():
            if dev.get("home_id") == home_id and dev.get("device_name", "").strip().lower() == accessory_name.lower():
                matches.append((did, dev))

        if not matches:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_name}' not found in home '{home_name}'"})
        if len(matches) > 1:
            return json.dumps({"success": False, "error": f"Multiple accessories named '{accessory_name}' found in home '{home_name}'"})

        accessory_id, device = matches[0]
        status = device.get("status", "offline")
        reachable = status == "online"

        return json.dumps({
            "success": True,
            "accessory_id": accessory_id,
            "accessory_name": device.get("device_name"),
            "reachable": reachable,
            "status": status,
            "last_seen": device.get("last_seen"),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_accessory_reachability",
                "description": "Check if an accessory is reachable (online).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "accessory_name": {
                            "type": "string",
                            "description": "Name of the accessory within the home.",
                        },
                    },
                    "required": ["home_name", "accessory_name"],
                },
            },
        }

