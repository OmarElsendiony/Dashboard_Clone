import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class GetDevice(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        device_name: str,
        household_id: str,
    ) -> str:

        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid devices container: expected dict at data['devices']",
                }
            )

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid homes container: expected dict at data['homes']",
                }
            )

        rooms_dict = data.get("rooms", {})
        if not isinstance(rooms_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid rooms container: expected dict at data['rooms']",
                }
            )

        # Validate required parameters
        if not device_name:
            return json.dumps({"success": False, "error": "device_name is required"})

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        # Convert to strings for consistent comparison
        device_name_str = str(device_name).strip()
        household_id_str = str(household_id).strip()

        # Check if household exists
        if household_id_str not in homes_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Household with ID '{household_id_str}' not found",
                }
            )

        home_info = homes_dict[household_id_str]
        if not isinstance(home_info, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid household data for ID '{household_id_str}'",
                }
            )

        # Find device by name in the specified household
        device_id = None
        device_info = None
        for did, device in devices_dict.items():
            if not isinstance(device, dict):
                continue

            if (
                str(device.get("home_id")) == household_id_str
                and str(device.get("device_name", "")).strip() == device_name_str
            ):
                device_id = str(did)
                device_info = device.copy()
                device_info["device_id"] = device_id
                break

        if device_info is None:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Device with name '{device_name_str}' not found in household '{household_id_str}'",
                }
            )

        # Get room information if device is assigned to a room
        room_info = None
        room_id = device_info.get("room_id")
        if room_id:
            room_id_str = str(room_id)
            if room_id_str in rooms_dict:
                room = rooms_dict[room_id_str]
                if isinstance(room, dict):
                    room_info = {
                        "room_id": room_id_str,
                        "room_name": room.get("room_name"),
                        "room_type": room.get("room_type"),
                    }

        room_info_return = room_info.copy()
        room_info_return["area_id"] = room_info_return.pop("room_id")
        room_info_return["area_name"] = room_info_return.pop("room_name")
        room_info_return["area_type"] = room_info_return.pop("room_type")

        return json.dumps(
            {
                "success": True,
                "device": device_info,
                "area": room_info_return,
                "message": f"Device '{device_name_str}' found successfully in household '{home_info.get('home_name')}'",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_device",
                "description": (
                    "Retrieve device information by device name and household ID. "
                    "Returns device details including device_id, device_type, status (online/offline), "
                    "area_id, serial_number, support_automation flag, and timestamps. "
                    "Also returns associated area information if the device is assigned to a area. "
                    "Validates that the household exists. "
                    "Returns an error if the household doesn't exist or the device is not found in the specified household."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_name": {
                            "type": "string",
                            "description": "The name of the device to retrieve.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household where the device is located.",
                        },
                    },
                    "required": ["device_name", "household_id"],
                },
            },
        }