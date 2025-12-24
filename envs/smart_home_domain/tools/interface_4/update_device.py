import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateDevice(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        device_id: str,
        household_id: str,
        device_name: Optional[str] = None,
        area_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

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
        if not device_id:
            return json.dumps({"success": False, "error": "device_id is required"})

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        # Convert to strings for consistent comparison
        device_id_str = str(device_id).strip()
        household_id_str = str(household_id).strip()
        device_name_str = str(device_name).strip() if device_name else None
        area_id_str = str(area_id).strip() if area_id else None
        status_str = str(status).strip() if status else None

        # Validate household exists
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

        # Check if device exists
        if device_id_str not in devices_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Device with ID '{device_id_str}' not found",
                }
            )

        device = devices_dict[device_id_str]
        if not isinstance(device, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid device data for ID '{device_id_str}'",
                }
            )

        # Verify device belongs to the specified household
        if str(device.get("home_id")) != household_id_str:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Device '{device_id_str}' does not belong to household '{household_id_str}'",
                }
            )

        # Validate status if provided
        if status_str:
            valid_statuses = ["online", "offline"]
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )

        # Validate area exists if area_id is provided
        if area_id_str and area_id_str != "":
            if area_id_str not in rooms_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Area with ID '{area_id_str}' not found",
                    }
                )

            room_info = rooms_dict[area_id_str]
            if not isinstance(room_info, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid area data for ID '{area_id_str}'",
                    }
                )

            # Verify the room belongs to the specified household
            if str(room_info.get("home_id")) != household_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Area '{area_id_str}' does not belong to household '{household_id_str}'",
                    }
                )

        # Check if new device_name conflicts with existing devices (excluding current device)
        if device_name_str:
            for did, dev in devices_dict.items():
                if not isinstance(dev, dict):
                    continue

                # Skip the current device being updated
                if str(did) == device_id_str:
                    continue

                if (
                    str(dev.get("home_id")) == household_id_str
                    and str(dev.get("device_name", "")).strip() == device_name_str
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Device with name '{device_name_str}' already exists in household '{household_id_str}' (device_id: {did})",
                        }
                    )

        # Update device fields
        updates_made = []

        if device_name_str:
            device["device_name"] = device_name_str
            updates_made.append(f"device_name to '{device_name_str}'")

        if area_id_str is not None:
            # Allow empty string to unassign from area
            device["room_id"] = area_id_str if area_id_str != "" else None
            if area_id_str == "":
                updates_made.append("unassigned from area")
            else:
                updates_made.append(f"area_id to '{area_id_str}'")

        if status_str:
            device["status"] = status_str
            updates_made.append(f"status to '{status_str}'")

            # Update last_seen timestamp if device is now online
            if status_str == "online":
                device["last_seen"] = timestamp

        # Update timestamp
        device["updated_at"] = timestamp

        if not updates_made:
            return json.dumps(
                {
                    "success": False,
                    "error": "No updates provided. At least one of device_name, area_id, or status must be specified.",
                }
            )
        
        device_return = device.copy()
        device_return["area_id"] = device_return.pop("room_id")

        return json.dumps(
            {
                "success": True,
                "device": device_return,
                "message": f"Device '{device.get('device_name')}' successfully updated. Changes: {', '.join(updates_made)}",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_device",
                "description": (
                    "Update device information including name, area assignment, and status. "
                    "Validates that the device exists in the specified household. "
                    "If device_name is provided, ensures it's unique within the household (excluding the current device). "
                    "If area_id is provided, validates that the area exists and belongs to the household. "
                    "Use empty string for area_id to unassign the device from any area. "
                    "If status is provided, validates it's either 'online' or 'offline'. "
                    "Updates last_seen timestamp when status is changed to 'online'. "
                    "At least one of device_name, area_id, or status must be provided for update. "
                    "Returns the updated device details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to update.",
                        },
                        "device_name": {
                            "type": "string",
                            "description": "Optional. The new name for the device. Must be unique within the household.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household the device belongs to.",
                        },
                        "area_id": {
                            "type": "string",
                            "description": "Optional. The ID of the area to assign the device to. Use empty string to unassign from any area.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. The new status of the device. Accepted values: 'online', 'offline'.",
                        },
                    },
                    "required": ["device_id", "household_id"],
                },
            },
        }
