import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class CommissionDevice(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        device_name: str,
        device_type: str,
        zone_id: str = None,
        status: str = "online",
        serial_number: str = None,
        support_automation: bool = False,
    ) -> str:
        """
        Add a new device entry to the devices table. Validates the household, ensures the device name
        is unique within that household, enforces the device_type/status enums, and optionally associates
        the device to a zone (room) if zone_id is provided.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            homes = data.get("homes")
            devices = data.get("devices")
            rooms = data.get("rooms")
            if not isinstance(homes, dict) or not isinstance(devices, dict) or not isinstance(rooms, dict):
                return json.dumps({"success": False, "error": "homes, devices, or rooms table missing/invalid."})

            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps({"success": False, "error": "home_id is required."})
            target_home_id = home_id.strip()
            home_record = homes.get(target_home_id)
            if not isinstance(home_record, dict):
                return json.dumps({"success": False, "error": "Household not found."})

            if not isinstance(device_name, str) or not device_name.strip():
                return json.dumps({"success": False, "error": "device_name is required."})
            device_name_clean = device_name.strip()

            allowed_types = {
                "camera",
                "bulb",
                "thermostat",
                "speaker",
                "door_lock",
                "motion_sensor",
                "temperature_sensor",
                "humidity_sensor",
                "light_sensor",
                "door_sensor",
                "water_leak_sensor",
                "smoke_detector_sensor",
                "power_outlet",
                "air_conditioner",
            }
            if not isinstance(device_type, str) or device_type.strip().lower() not in allowed_types:
                return json.dumps({"success": False, "error": "device_type must be a supported enum value."})
            device_type_clean = device_type.strip().lower()

            allowed_status = {"online", "offline"}
            status_clean = status.strip().lower() if isinstance(status, str) and status.strip() else "online"
            if status_clean not in allowed_status:
                return json.dumps({"success": False, "error": "status must be 'online' or 'offline'."})

            zone_id_clean = None
            if zone_id is not None:
                if not isinstance(zone_id, str) or not zone_id.strip():
                    return json.dumps({"success": False, "error": "zone_id cannot be empty when provided."})
                zone_id_clean = zone_id.strip()
                zone_record = rooms.get(zone_id_clean)
                if not isinstance(zone_record, dict) or str(zone_record.get("home_id")) != target_home_id:
                    return json.dumps({"success": False, "error": "zone_id does not belong to the household."})

            for record in devices.values():
                if not isinstance(record, dict):
                    continue
                if str(record.get("home_id")) == target_home_id and record.get("device_name", "").lower() == device_name_clean.lower():
                    return json.dumps({"success": False, "error": "Device name must be unique within the household."})

            numeric_ids = []
            for key in devices.keys():
                try:
                    numeric_ids.append(int(key))
                except (TypeError, ValueError):
                    continue
            new_device_id = str(max(numeric_ids, default=0) + 1)

            record = {
                "device_id": new_device_id,
                "home_id": target_home_id,
                "zone_id": zone_id_clean,
                "device_name": device_name_clean,
                "device_type": device_type_clean,
                "serial_number": serial_number.strip() if isinstance(serial_number, str) and serial_number.strip() else None,
                "status": status_clean,
                "support_automation": bool(support_automation),
                "installed_at": "2025-12-19T23:59:00",
                "last_seen": None,
                "created_at": "2025-12-19T23:59:00",
                "updated_at": "2025-12-19T23:59:00",
            }
            devices[new_device_id] = record

            return json.dumps({"success": True, "device": record})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"commission_device failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "commission_device",
                "description": (
                    "Onboard a new device into a household. Requires home_id, device_name, and device_type. "
                    "Optional zone_id, status (online/offline), serial_number, and support_automation."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Required. Household identifier where the device is commissioned.",
                        },
                        "device_name": {
                            "type": "string",
                            "description": "Required. Unique device name within the household.",
                        },
                        "device_type": {
                            "type": "string",
                            "description": (
                                "Required. Device type enum value: camera, bulb, thermostat, speaker, door_lock, "
                                "motion_sensor, temperature_sensor, humidity_sensor, light_sensor, door_sensor, "
                                "water_leak_sensor, smoke_detector_sensor, power_outlet, air_conditioner."
                            ),
                        },
                        "zone_id": {
                            "type": "string",
                            "description": "Optional. Room/zone ID where the device should be placed.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. Device status enum: online or offline (defaults to online).",
                        },
                        "serial_number": {
                            "type": "string",
                            "description": "Optional. Device serial number.",
                        },
                        "support_automation": {
                            "type": "boolean",
                            "description": "Optional. Indicates if the device supports automation (defaults to false).",
                        },
                    },
                    "required": ["home_id", "device_name", "device_type"],
                },
            },
        }
