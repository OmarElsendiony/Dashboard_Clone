import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class RemoveAccessoryFromRoom(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        accessory_id: str,
    ) -> str:
        """
        Unassign an accessory from its room. Accessory must belong to the specified home.
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

        if not isinstance(accessory_id, str) or not accessory_id.strip():
            return json.dumps({"success": False, "error": "accessory_id must be provided"})
        accessory_id = accessory_id.strip()

        if accessory_id not in devices:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' not found"})

        device = devices[accessory_id]
        
        # Verify accessory belongs to the specified home
        if device.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' does not belong to home '{home_name}'"})
        
        if device.get("room_id") is None:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' is not assigned to any room"})

        device["room_id"] = None
        device["updated_at"] = "2025-12-19T23:59:00"

        return json.dumps({
            "success": True,
            "accessory": {
                "accessory_id": device.get("device_id") or accessory_id,
                "accessory_name": device.get("device_name"),
                "accessory_type": device.get("device_type"),
                "room_id": device.get("room_id"),
                "serial_number": device.get("serial_number"),
                "status": device.get("status"),
                "support_automation": device.get("support_automation"),
                "installed_at": device.get("installed_at"),
                "last_seen": device.get("last_seen"),
                "created_at": device.get("created_at"),
                "updated_at": device.get("updated_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "remove_accessory_from_room",
                "description": "Remove an accessory from its assigned room. Accessory must belong to the specified home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "accessory_id": {
                            "type": "string",
                            "description": "Identifier of the accessory to unassign.",
                        },
                    },
                    "required": ["home_name", "accessory_id"],
                },
            },
        }

