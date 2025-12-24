import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class RenameDeviceIdentity(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        device_name: str,
        new_device_name: str,
        device_id: str = None,
    ) -> str:
        """
        Rename a device within a household. home_id and device_name locate the device unless device_id is provided.
        Ensures the new name is unique within the household before updating the record.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            homes = data.get("homes")
            devices = data.get("devices")
            if not isinstance(homes, dict) or not isinstance(devices, dict):
                return json.dumps({"success": False, "error": "homes or devices table missing/invalid."})

            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps({"success": False, "error": "home_id is required."})
            target_home_id = home_id.strip()
            if target_home_id not in homes:
                return json.dumps({"success": False, "error": "Household not found."})

            if not isinstance(device_name, str) or not device_name.strip():
                return json.dumps({"success": False, "error": "device_name is required."})
            device_name_cmp = device_name.strip().lower()

            if not isinstance(new_device_name, str) or not new_device_name.strip():
                return json.dumps({"success": False, "error": "new_device_name is required."})
            new_name_cmp = new_device_name.strip().lower()

            target_record = None
            if isinstance(device_id, str) and device_id.strip():
                target_record = devices.get(device_id.strip())
                if target_record and str(target_record.get("home_id")) != target_home_id:
                    target_record = None
            if target_record is None:
                for record in devices.values():
                    if not isinstance(record, dict):
                        continue
                    if str(record.get("home_id")) == target_home_id and record.get("device_name", "").lower() == device_name_cmp:
                        target_record = record
                        break

            if not isinstance(target_record, dict):
                return json.dumps({"success": False, "error": "Device not found in the specified household."})

            for record in devices.values():
                if not isinstance(record, dict):
                    continue
                if record is target_record:
                    continue
                if str(record.get("home_id")) == target_home_id and record.get("device_name", "").lower() == new_name_cmp:
                    return json.dumps({"success": False, "error": "new_device_name must be unique within the household."})

            target_record["device_name"] = new_device_name.strip()
            target_record["updated_at"] = "2025-12-19T23:59:00"
            target_record["zone_id"] = target_record.pop("room_id", None)

            return json.dumps({"success": True, "device": target_record})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"rename_device_identity failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "rename_device_identity",
                "description": (
                    "Rename a device inside a household. Requires home_id, device_name, and new_device_name; "
                    "device_id can be supplied to disambiguate."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Required. Household identifier.",
                        },
                        "device_name": {
                            "type": "string",
                            "description": "Required. Current device name.",
                        },
                        "new_device_name": {
                            "type": "string",
                            "description": "Required. New device name (must be unique within the household).",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Optional. Device identifier for direct lookup.",
                        },
                    },
                    "required": ["home_id", "device_name", "new_device_name"],
                },
            },
        }
