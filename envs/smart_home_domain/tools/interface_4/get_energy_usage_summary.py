import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
from datetime import datetime

class GetEnergyUsageSummary(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        household_id: str,
        target_date: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
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

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid devices container: expected dict at data['devices']",
                }
            )

        energy_usage_dict = data.get("energy_usage", {})
        if not isinstance(energy_usage_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid energy_usage container: expected dict at data['energy_usage']",
                }
            )

        energy_tariffs_dict = data.get("energy_tariffs", {})
        if not isinstance(energy_tariffs_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid energy_tariffs container: expected dict at data['energy_tariffs']",
                }
            )

        # Validate required parameters
        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        if not target_date:
            return json.dumps({"success": False, "error": "target_date is required"})

        # Convert to strings for consistent comparison
        household_id_str = str(household_id).strip()
        target_date_str = str(target_date).strip()

        # Validate date format
        try:
            target_date_obj = datetime.strptime(target_date_str, "%Y-%m-%d")
        except ValueError:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid target_date format. Expected YYYY-MM-DD format. Got: {target_date_str}",
                }
            )

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

        # Get all online devices for this household
        online_devices = []
        for device_id, device in devices_dict.items():
            if not isinstance(device, dict):
                continue

            if (
                str(device.get("home_id")) == household_id_str
                and str(device.get("status")) == "online"
            ):
                online_devices.append(
                    {
                        "device_id": str(device_id),
                        "device_name": device.get("device_name"),
                        "device_type": device.get("device_type"),
                    }
                )

        # Get energy usage for the target date
        device_usage_breakdown = []
        total_energy_kwh = 0.0

        for device in online_devices:
            device_id = device["device_id"]
            device_energy = 0.0

            # Find energy usage records for this device and date
            for usage_id, usage in energy_usage_dict.items():
                if not isinstance(usage, dict):
                    continue

                if (
                    str(usage.get("device_id")) == device_id
                    and str(usage.get("usage_date")) == target_date_str
                ):
                    try:
                        power_consumed = float(usage.get("power_consumed_kWh", 0))
                        device_energy += power_consumed
                    except (ValueError, TypeError):
                        continue

            if device_energy > 0:
                device_usage_breakdown.append(
                    {
                        "device_id": device_id,
                        "device_name": device["device_name"],
                        "device_type": device["device_type"],
                        "energy_consumed_kwh": round(device_energy, 2),
                    }
                )
                total_energy_kwh += device_energy

        # Find applicable tariff for the target date
        applicable_tariff = None
        for tariff_id, tariff in energy_tariffs_dict.items():
            if not isinstance(tariff, dict):
                continue

            if str(tariff.get("home_id")) != household_id_str:
                continue

            effective_from = str(tariff.get("effective_from", ""))
            effective_until = tariff.get("effective_until")

            try:
                effective_from_obj = datetime.strptime(effective_from, "%Y-%m-%d")

                # Check if target_date is within the tariff's validity period
                if target_date_obj >= effective_from_obj:
                    # If effective_until is None, tariff is ongoing
                    if effective_until is None:
                        applicable_tariff = tariff
                        break
                    else:
                        effective_until_obj = datetime.strptime(
                            str(effective_until), "%Y-%m-%d"
                        )
                        if target_date_obj <= effective_until_obj:
                            applicable_tariff = tariff
                            break
            except (ValueError, TypeError):
                continue

        # Calculate cost based on tariff
        estimated_cost = 0.0
        tariff_info = None

        if applicable_tariff:
            try:
                rate_per_kwh = float(applicable_tariff.get("rate_per_kWh", 0))
                estimated_cost = total_energy_kwh * rate_per_kwh
                tariff_info = {
                    "tariff_id": str(
                        [
                            tid
                            for tid, t in energy_tariffs_dict.items()
                            if t == applicable_tariff
                        ][0]
                    ),
                    "tariff_name": applicable_tariff.get("tariff_name"),
                    "rate_per_kwh": rate_per_kwh,
                }
            except (ValueError, TypeError, IndexError):
                pass

        energy_summary = {
            "household_id": household_id_str,
            "household_name": home_info.get("home_name"),
            "target_date": target_date_str,
            "total_energy_consumed_kwh": round(total_energy_kwh, 2),
            "estimated_cost": round(estimated_cost, 2) if tariff_info else None,
            "currency": "USD" if tariff_info else None,
            "tariff_applied": tariff_info,
            "online_devices_count": len(online_devices),
            "devices_with_usage_count": len(device_usage_breakdown),
            "device_breakdown": device_usage_breakdown,
        }

        return json.dumps(
            {
                "success": True,
                "energy_summary": energy_summary,
                "message": f"Energy usage summary retrieved for household '{home_info.get('home_name')}' on {target_date_str}",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_energy_usage_summary",
                "description": (
                    "Get energy usage summary for all devices in a household for a specific date. "
                    "Retrieves energy consumption data only for online devices. "
                    "Calculates total energy consumption in kWh and estimated cost based on the applicable energy tariff. "
                    "The tariff is selected based on the target_date falling within the tariff's effective date range "
                    "(between effective_from and effective_until, or ongoing if effective_until is null). "
                    "Returns a detailed breakdown by device including device_id, device_name, device_type, and energy consumed. "
                    "Also includes tariff information used for cost calculation. "
                    "Validates that the household exists and target_date is in YYYY-MM-DD format."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household to get energy usage summary for.",
                        },
                        "target_date": {
                            "type": "string",
                            "description": "The date to get energy usage for in YYYY-MM-DD format.",
                        },
                    },
                    "required": ["household_id", "target_date"],
                },
            },
        }
