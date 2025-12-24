import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool


class DiscoverHouseholdDevices(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        zone_id: str = None,
        device_name: str = None,
        device_type: str = None,
        status: str = None,
    ) -> str:
        """
        Return the devices that belong to the given household along with their states and attributes. Filters by optional zone_id (room_id), device name/type,
        and status, and also exposes support_sensor_automation when the device type contains 'sensor'.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            homes = data.get("homes")
            devices = data.get("devices")
            device_states = data.get("device_states", {})
            device_state_attributes = data.get("device_state_attributes", {})
            if not isinstance(homes, dict) or not isinstance(devices, dict):
                return json.dumps({"success": False, "error": "homes or devices table missing/invalid."})

            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps({"success": False, "error": "home_id is required."})

            target_home_id = home_id.strip()
            if target_home_id not in homes:
                return json.dumps({"success": False, "error": "Household not found."})

            zone_cmp = zone_id.strip() if isinstance(zone_id, str) and zone_id.strip() else None
            name_cmp = device_name.strip().lower() if isinstance(device_name, str) and device_name.strip() else None
            type_cmp = None
            if device_type is not None:
                if not isinstance(device_type, str) or not device_type.strip():
                    return json.dumps({"success": False, "error": "device_type cannot be empty when provided."})
                type_cmp = device_type.strip().lower()
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
                if type_cmp not in allowed_types:
                    return json.dumps({"success": False, "error": "device_type is not supported."})

            status_cmp = None
            if status is not None:
                if not isinstance(status, str) or not status.strip():
                    return json.dumps({"success": False, "error": "status cannot be empty when provided."})
                status_cmp = status.strip().lower()
                if status_cmp not in {"online", "offline"}:
                    return json.dumps({"success": False, "error": "status must be 'online' or 'offline'."})
            else:
                status_cmp = "online"

            matched_devices: List[Dict[str, Any]] = []
            for record in devices.values():
                if not isinstance(record, dict):
                    continue
                if str(record.get("home_id")) != target_home_id:
                    continue
                if zone_cmp and str(record.get("room_id")) != zone_cmp:
                    continue
                if name_cmp and record.get("device_name", "").lower() != name_cmp:
                    continue
                if type_cmp and record.get("device_type", "").lower() != type_cmp:
                    continue
                record_status = record.get("status", "")
                if status_cmp and record_status.lower() != status_cmp:
                    continue
                support_sensor = "sensor" in (record.get("device_type", "").lower())
                device_id_clean = record.get("device_id")
                states_payload = []
                for state in device_states.values():
                    if not isinstance(state, dict):
                        continue
                    if str(state.get("device_id", "")).strip() != str(device_id_clean):
                        continue
                    state_id = state.get("state_id")
                    attributes_payload = []
                    for attr in device_state_attributes.values():
                        if not isinstance(attr, dict):
                            continue
                        if str(attr.get("state_id", "")).strip() != str(state_id):
                            continue
                        attributes_payload.append(
                            {
                                "attribute_id": attr.get("attribute_id"),
                                "attribute_name": attr.get("attribute_name"),
                                "attribute_value": attr.get("attribute_value"),
                                "created_at": attr.get("created_at"),
                            }
                        )
                    states_payload.append(
                        {
                            "state_id": state_id,
                            "changed_at": state.get("changed_at"),
                            "created_at": state.get("created_at"),
                            "attributes": attributes_payload,
                        }
                    )

                matched_devices.append(
                    {
                        "device_id": record.get("device_id"),
                        "device_name": record.get("device_name"),
                        "device_type": record.get("device_type"),
                        "zone_id": record.get("room_id"),
                        "status": record.get("status"),
                        "support_automation": record.get("support_automation"),
                        "support_sensor_automation": support_sensor,
                        "last_seen": record.get("last_seen"),
                        "states": states_payload,
                    }
                )

            return json.dumps({"success": True, "devices": matched_devices})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"discover_household_devices failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "discover_household_devices",
                "description": (
                    "List the devices belonging to a household. Returns only online devices by default."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Required. Household id to retrieve devices.",
                        },
                        "zone_id": {
                            "type": "string",
                            "description": "Optional. Filter devices in a specific zone.",
                        },
                        "device_name": {
                            "type": "string",
                            "description": "Optional. Device name.",
                        },
                        "device_type": {
                            "type": "string",
                            "description": (
                                "Optional. Device type enum value: camera, bulb, thermostat, speaker, door_lock, "
                                "motion_sensor, temperature_sensor, humidity_sensor, light_sensor, door_sensor, "
                                "water_leak_sensor, smoke_detector_sensor, power_outlet, air_conditioner."
                            ),
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. Device status enum: online or offline.",
                        },
                    },
                    "required": ["home_id"],
                },
            },
        }
