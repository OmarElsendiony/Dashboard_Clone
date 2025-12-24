import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class AddDevice(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        household_id: str,
        device_name: str,
        device_type: str,
        status: str,
        serial_number: Optional[str] = None,
        area_id: Optional[str] = None,
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
        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        if not device_name:
            return json.dumps({"success": False, "error": "device_name is required"})

        if not device_type:
            return json.dumps({"success": False, "error": "device_type is required"})

        if not status:
            return json.dumps({"success": False, "error": "status is required"})

        # Convert to strings for consistent comparison
        household_id_str = str(household_id).strip()
        device_name_str = str(device_name).strip()
        device_type_str = str(device_type).strip()
        status_str = str(status).strip()
        area_id_str = str(area_id).strip() if area_id else None
        serial_number_str = str(serial_number).strip() if serial_number else None

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

        # Validate device_type
        valid_device_types = [
            "camera", "bulb", "thermostat", "speaker", "door_lock",
            "motion_sensor", "temperature_sensor", "humidity_sensor",
            "light_sensor", "door_sensor", "water_leak_sensor",
            "smoke_detector_sensor", "power_outlet", "air_conditioner"
        ]
        if device_type_str not in valid_device_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid device_type '{device_type_str}'. Must be one of: {', '.join(valid_device_types)}",
                }
            )

        # Validate status
        valid_statuses = ["online", "offline"]
        if status_str not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Validate area exists if area_id is provided
        if area_id_str:
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

        # Check if device_name already exists in this household
        for did, device in devices_dict.items():
            if not isinstance(device, dict):
                continue

            if (
                str(device.get("home_id")) == household_id_str
                and str(device.get("device_name", "")).strip() == device_name_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device with name '{device_name_str}' already exists in household '{household_id_str}' (device_id: {did})",
                    }
                )

        # Check if serial_number is unique (if provided)
        if serial_number_str:
            for did, device in devices_dict.items():
                if not isinstance(device, dict):
                    continue

                existing_serial = device.get("serial_number")
                if existing_serial and str(existing_serial).strip() == serial_number_str:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Device with serial number '{serial_number_str}' already exists (device_id: {did})",
                        }
                    )

        # Generate new device_id
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_device_id = generate_id(devices_dict)

        # Create new device entry
        new_device = {
            "device_id": new_device_id,
            "home_id": household_id_str,
            "room_id": area_id_str,
            "device_name": device_name_str,
            "device_type": device_type_str,
            "serial_number": serial_number_str,
            "status": status_str,
            "support_automation": True,
            "installed_at": timestamp,
            "last_seen": timestamp if status_str == "online" else None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        new_device_return = new_device.copy()
        new_device_return.pop("room_id")
        new_device_return["area_id"] = area_id_str

        # Add to data
        devices_dict[new_device_id] = new_device

        return json.dumps(
            {
                "success": True,
                "device": new_device_return,
                "message": f"Device '{device_name_str}' successfully added to household '{home_info.get('home_name')}' with ID: {new_device_id}",
                "household_name": home_info.get("home_name"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_device",
                "description": (
                    "Register/onboard a new device into the smart home ecosystem. "
                    "Creates a new device entry for a household with the specified attributes. "
                    "Validates that the household exists and the device_type is valid. "
                    "Valid device types: camera, bulb, thermostat, speaker, door_lock, motion_sensor, "
                    "temperature_sensor, humidity_sensor, light_sensor, door_sensor, water_leak_sensor, "
                    "smoke_detector_sensor, power_outlet, air_conditioner. "
                    "If area_id is provided, validates that the area exists and belongs to the household. "
                    "Ensures device_name is unique within the household and serial_number is globally unique. "
                    "Status must be 'online' or 'offline'. "
                    "Returns the created device details including the generated device_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household to add the device to.",
                        },
                        "device_name": {
                            "type": "string",
                            "description": "The name of the device. Must be unique within the household.",
                        },
                        "area_id": {
                            "type": "string",
                            "description": "Optional. The ID of the area to assign the device to.",
                        },
                        "device_type": {
                            "type": "string",
                            "description": "The type of device. Accepted values: camera, bulb, thermostat, speaker, door_lock, motion_sensor, temperature_sensor, humidity_sensor, light_sensor, door_sensor, water_leak_sensor, smoke_detector_sensor, power_outlet, air_conditioner.",
                        },
                        "serial_number": {
                            "type": "string",
                            "description": "Optional. The serial number of the device. Must be globally unique. ",
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the device. Accepted values: 'online', 'offline'.",
                        },
                    },
                    "required": ["household_id", "device_name", "device_type", "status"],
                },
            },
        }