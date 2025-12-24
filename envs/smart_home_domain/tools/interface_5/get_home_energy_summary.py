import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetHomeEnergySummary(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        """
        Retrieve aggregated energy usage for a home within a date range.
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

        home_device_ids = {dev_id for dev_id, dev in devices.items() if dev.get("home_id") == home_id}

        accessory_usage = {}
        total_kwh = 0.0

        for usage in energy_usage.values():
            device_id = usage.get("device_id")
            if device_id in home_device_ids:
                usage_date = usage.get("usage_date")
                
                if start_filter and usage_date < start_filter:
                    continue
                if end_filter and usage_date > end_filter:
                    continue
                
                try:
                    kwh = float(usage.get("power_consumed_kWh", 0))
                except (ValueError, TypeError):
                    kwh = 0.0
                
                if device_id not in accessory_usage:
                    accessory_usage[device_id] = {
                        "accessory_id": device_id,
                        "accessory_name": devices[device_id].get("device_name"),
                        "accessory_type": devices[device_id].get("device_type"),
                        "total_kWh": 0.0,
                    }
                
                accessory_usage[device_id]["total_kWh"] += kwh
                total_kwh += kwh

        for dev_id in accessory_usage:
            accessory_usage[dev_id]["total_kWh"] = round(accessory_usage[dev_id]["total_kWh"], 2)

        return json.dumps({
            "success": True,
            "home_name": home_name,
            "accessory_summary": list(accessory_usage.values()),
            "total_home_consumption_kWh": round(total_kwh, 2),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_home_energy_summary",
                "description": "Get energy usage summary for all devices in a home within an optional date range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
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
                    "required": ["home_name"],
                },
            },
        }

