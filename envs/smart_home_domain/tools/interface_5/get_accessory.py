import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class GetAccessory(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        accessory_id: str,
    ) -> str:
        """
        Retrieve accessory details including its current state.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        devices = data.get("devices")
        device_states = data.get("device_states")
        device_state_attributes = data.get("device_state_attributes")

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
        if device.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' does not belong to home '{home_name}'"})

        current_state = None
        if isinstance(device_states, dict) and isinstance(device_state_attributes, dict):
            latest_state_id = None
            latest_time = None
            for state_id, state in device_states.items():
                if state.get("device_id") == accessory_id:
                    changed_at = state.get("changed_at")
                    if latest_time is None or (changed_at and changed_at > latest_time):
                        latest_time = changed_at
                        latest_state_id = state_id

            if latest_state_id:
                attributes = {}
                for attr in device_state_attributes.values():
                    if attr.get("state_id") == latest_state_id:
                        attributes[attr.get("attribute_name")] = attr.get("attribute_value")
                current_state = {
                    "state_id": latest_state_id,
                    "changed_at": latest_time,
                    "attributes": attributes,
                }

        result = dict(device)
        result["current_state"] = current_state

        # Return SOP terminology only (do not leak DB field names)
        presented = {
            "accessory_id": result.get("device_id") or accessory_id,
            "accessory_name": result.get("device_name"),
            "accessory_type": result.get("device_type"),
            "room_id": result.get("room_id"),
            "serial_number": result.get("serial_number"),
            "status": result.get("status"),
            "support_automation": result.get("support_automation"),
            "installed_at": result.get("installed_at"),
            "last_seen": result.get("last_seen"),
            "created_at": result.get("created_at"),
            "updated_at": result.get("updated_at"),
            "current_state": (None if not isinstance(current_state, dict) else {
                "changed_at": current_state.get("changed_at"),
                "attributes": current_state.get("attributes"),
            }),
        }

        return json.dumps({"success": True, "accessory": presented})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_accessory",
                "description": "Get detailed information about a specific accessory including its current state.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "accessory_id": {
                            "type": "string",
                            "description": "Identifier of the accessory.",
                        },
                    },
                    "required": ["home_name", "accessory_id"],
                },
            },
        }

