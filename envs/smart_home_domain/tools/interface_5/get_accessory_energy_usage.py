import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetAccessoryEnergyUsage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        accessory_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        """
        Retrieve energy usage records for a accessory within a date range.
        """

        def validate_date(date_str: str) -> bool:
            if not isinstance(date_str, str):
                return False
            parts = date_str.split("-")
            if len(parts) != 3:
                return False
            try:
                year, month, day = map(int, parts)
                return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31
            except ValueError:
                return False

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        devices = data.get("devices")
        energy_usage = data.get("energy_usage")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(devices, dict):
            return json.dumps({"success": False, "error": "devices store missing"})
        if not isinstance(energy_usage, dict):
            return json.dumps({"success": False, "error": "energy_usage store missing"})

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

        if devices[accessory_id].get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Accessory '{accessory_id}' does not belong to home '{home_name}'"})

        start_filter = None
        if start_date:
            if not validate_date(start_date):
                return json.dumps({"success": False, "error": "start_date must be in format YYYY-MM-DD"})
            start_filter = start_date

        end_filter = None
        if end_date:
            if not validate_date(end_date):
                return json.dumps({"success": False, "error": "end_date must be in format YYYY-MM-DD"})
            end_filter = end_date

        # If both are provided, start_date must not be after end_date
        if start_filter and end_filter and start_filter > end_filter:
            return json.dumps({"success": False, "error": "start_date must be less than or equal to end_date"})

        result_usage = []
        total_kwh = 0.0

        for usage in energy_usage.values():
            if usage.get("device_id") == accessory_id:
                usage_date = usage.get("usage_date")
                
                if start_filter and usage_date < start_filter:
                    continue
                if end_filter and usage_date > end_filter:
                    continue
                
                # Return SOP terminology only (do not leak DB field names)
                result_usage.append({
                    "usage_id": usage.get("usage_id"),
                    "accessory_id": usage.get("device_id"),
                    "usage_date": usage.get("usage_date"),
                    "power_consumed_kWh": usage.get("power_consumed_kWh"),
                    "created_at": usage.get("created_at"),
                })
                try:
                    total_kwh += float(usage.get("power_consumed_kWh", 0))
                except (ValueError, TypeError):
                    pass

        return json.dumps({
            "success": True,
            "accessory_id": accessory_id,
            "usage_records": result_usage,
            "total_power_consumed_kWh": round(total_kwh, 2),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_accessory_energy_usage",
                "description": "Get energy usage data for a accessory within an optional date range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "accessory_id": {
                            "type": "string",
                            "description": "Identifier of the accessory. The accessory must belong to the specified home.",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Optional start date in format YYYY-MM-DD.",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Optional end date in format YYYY-MM-DD.",
                        },
                    },
                    "required": ["home_name", "accessory_id"],
                },
            },
        }

