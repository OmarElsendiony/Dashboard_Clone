import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class GenerateEnergyInsights(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        target_date: Optional[str] = None,
    ) -> str:

        """Generate energy insights (total usage, comparison, and top consumers) for a household."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {"success": False, "error": "Invalid payload: data must be dict."}
                )

            homes = data.get("homes")
            devices = data.get("devices")
            energy_usage = data.get("energy_usage")
            energy_tariffs = data.get("energy_tariffs")

            if (
                not isinstance(homes, dict)
                or not isinstance(devices, dict)
                or not isinstance(energy_usage, dict)
                or not isinstance(energy_tariffs, dict)
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing homes/devices/energy_usage/energy_tariffs collections in dataset.",
                    }
                )

            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps(
                    {"success": False, "error": "home_id is required to scope the insights."}
                )
            home_id_clean = home_id.strip()
            if home_id_clean not in homes:
                return json.dumps({"success": False, "error": "Home not found."})

            devices_in_home = {
                device_id
                for device_id, record in devices.items()
                if isinstance(record, dict) and str(record.get("home_id", "")).strip() == home_id_clean
            }
            usage_entries = [
                record
                for record in energy_usage.values()
                if isinstance(record, dict)
                and str(record.get("device_id", "")).strip() in devices_in_home
            ]
            if not usage_entries:
                return json.dumps(
                    {"success": False, "error": "No energy usage data found for this home."}
                )

            def _valid_date(text: str) -> bool:
                return len(text) == 10 and text[4] == "-" and text[7] == "-"

            if target_date:
                if not isinstance(target_date, str) or not target_date.strip():
                    return json.dumps(
                        {"success": False, "error": "target_date must be a YYYY-MM-DD string when provided."}
                    )
                if not _valid_date(target_date.strip()):
                    return json.dumps(
                        {"success": False, "error": "target_date must follow YYYY-MM-DD format."}
                    )
                target_date_clean = target_date.strip()
            else:
                target_date_clean = max(
                    str(entry.get("usage_date", "")).strip() for entry in usage_entries if entry.get("usage_date")
                )

            try:
                target_dt = datetime.strptime(target_date_clean, "%Y-%m-%d")
            except ValueError:
                return json.dumps(
                    {"success": False, "error": "target_date must follow YYYY-MM-DD format."}
                )
            previous_date_clean = (target_dt - timedelta(days=1)).strftime("%Y-%m-%d")

            def _collect_for(day: str) -> List[Dict[str, Any]]:
                return [
                    record
                    for record in usage_entries
                    if str(record.get("usage_date", "")).strip() == day
                ]

            current_records = _collect_for(target_date_clean)
            if not current_records:
                return json.dumps(
                    {"success": False, "error": "No usage data exists for the requested date."}
                )

            previous_records = _collect_for(previous_date_clean)

            def _sum_kwh(records: List[Dict[str, Any]]) -> float:
                total = 0.0
                for record in records:
                    total += float(record.get("power_consumed_kWh", 0.0))
                return total

            total_kwh = _sum_kwh(current_records)
            previous_kwh = _sum_kwh(previous_records)
            comparison_percent = None
            if previous_kwh > 0:
                comparison_percent = round(((total_kwh - previous_kwh) / previous_kwh) * 100, 2)

            home_tariffs = [
                entry
                for entry in energy_tariffs.values()
                if isinstance(entry, dict) and str(entry.get("home_id", "")).strip() == home_id_clean
            ]
            tariff_rate = None
            if home_tariffs:
                latest_tariff = max(
                    home_tariffs,
                    key=lambda entry: entry.get("updated_at") or entry.get("created_at") or "",
                )
                tariff_rate = float(latest_tariff.get("rate_per_kWh", 0.0))

            estimated_cost = round(total_kwh * tariff_rate, 2) if tariff_rate is not None else None

            device_totals: Dict[str, float] = {}
            for record in current_records:
                device_key = str(record.get("device_id", "")).strip()
                device_totals.setdefault(device_key, 0.0)
                device_totals[device_key] += float(record.get("power_consumed_kWh", 0.0))

            top_consumers = sorted(
                (
                    {
                        "device_id": device_id,
                        "device_name": devices.get(device_id, {}).get("device_name"),
                        "power_consumed_kWh": round(kwh, 3),
                    }
                    for device_id, kwh in device_totals.items()
                ),
                key=lambda entry: entry["power_consumed_kWh"],
                reverse=True,
            )[:3]

            insights_payload = {
                "total_kWh": round(total_kwh, 3),
                "previous_day_kWh": round(previous_kwh, 3),
                "comparison_vs_previous_day_percent": comparison_percent,
                "tariff_rate_per_kWh": tariff_rate,
                "estimated_cost": estimated_cost,
                "top_consumers": top_consumers,
            }

            return json.dumps(
                {
                    "success": True,
                    "home_id": home_id_clean,
                    "target_date": target_date_clean,
                    "insights": insights_payload,
                    "usage_records": current_records,
                }
            )

        except Exception as exc:
            return json.dumps(
                {"success": False, "error": f"Failed to generate energy insights: {exc}"}
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "generate_energy_insights",
                "description": (
                    "Generate energy insights (total usage, comparison, and top consumers) for a household. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Required household identifier.",
                        },
                        "target_date": {
                            "type": "string",
                            "description": "Optional YYYY-MM-DD date. Defaults to the latest usage date available.",
                        },
                    },
                    "required": ["home_id"],
                },
            },
        }
