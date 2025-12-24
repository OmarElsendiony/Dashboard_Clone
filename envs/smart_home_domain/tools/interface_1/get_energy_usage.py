import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetEnergyUsage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        homes = data.get("homes", {})
        home = {}
        if home_name:
            for h in homes.values():
                if h.get("home_name") == home_name:
                    home_id = h.get("home_id")
                    break
        if home_id:
            home = homes.get(home_id)
        if not home:
            return json.dumps({"success": False, "error": "Home not found"})
        if start_date and not end_date:
            return json.dumps(
                {
                    "success": False,
                    "error": "End date is required when start date is provided",
                }
            )
        if end_date and not start_date:
            return json.dumps(
                {
                    "success": False,
                    "error": "Start date is required when end date is provided",
                }
            )
        if start_date and end_date:
            # validate date format YYYY-MM-DD
            try:
                from datetime import datetime

                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                if start_dt > end_dt:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Start date must be before end date",
                        }
                    )
            except ValueError:
                return json.dumps(
                    {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
                )

        devices = data.get("devices", [])
        # filter devices by home_id
        home_devices = [
            d for d in devices.values() if d.get("home_id") == home.get("home_id")
        ]
        energy_usages = data.get("energy_usage", {})
        total_energy_usage = 0.0
        for device in home_devices:
            device_id = device.get("device_id")
            for record in energy_usages.values():
                if record.get("device_id") == device_id:
                    record_date = record.get("usage_date")
                    if start_date and end_date:
                        if start_date <= record_date <= end_date:
                            total_energy_usage += record.get("power_consumed_kWh", 0.0)
                    else:
                        total_energy_usage += record.get("power_consumed_kWh", 0.0)

        return json.dumps(
            {
                "success": True,
                "home_id": home.get("home_id"),
                "home_name": home.get("home_name"),
                "total_energy_usage_kWh": total_energy_usage,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_energy_usage",
                "description": "Retrieve energy usage data for a specified home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home to retrieve energy usage for.",
                        },
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home to retrieve energy usage for.",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "The start date for the energy usage data in YYYY-MM-DD format.",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "The end date for the energy usage data in YYYY-MM-DD format.",
                        },
                    },
                    "required": [],
                },
            },
        }
