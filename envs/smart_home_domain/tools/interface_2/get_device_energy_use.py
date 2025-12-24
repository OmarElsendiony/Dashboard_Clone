import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetDeviceEnergyUse(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
        device_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """
        Get energy usage data for devices with optional filters.
        
        Args:
            data: The data dictionary containing all smart home data.
            home_id: Filter by home ID (optional).
            home_name: Filter by home name (optional).
            device_id: Filter by specific device ID (optional).
            start_date: Start date for filtering usage records (format: YYYY-MM-DD, optional).
            end_date: End date for filtering usage records (format: YYYY-MM-DD, optional).
            
        Returns:
            JSON string containing list of energy usage records and total consumption.
        """
        energy_usage = data.get("energy_usage", {})
        devices = data.get("devices", {})
        homes = data.get("homes", {})
        energy_tariffs = data.get("energy_tariffs", {})
        
        # Resolve home_id from home_name if provided
        resolved_home_id = home_id
        if home_name and not resolved_home_id:
            for h_id, home in homes.items():
                if home.get("home_name") == home_name:
                    resolved_home_id = h_id
                    break
        
        results = []
        total_consumption = 0.0
        total_cost = 0.0
        
        for usage in energy_usage.values():
            usage_device_id = str(usage.get("device_id"))
            usage_date = usage.get("usage_date")
            power_consumed = usage.get("power_consumed_kWh", 0.0)
            
            # Filter by device_id
            if device_id is not None and usage_device_id != str(device_id):
                continue
            
            # Filter by home_id or home_name
            if resolved_home_id is not None:
                device = devices.get(usage_device_id)
                if not device or str(device.get("home_id")) != str(resolved_home_id):
                    continue
            
            # Filter by date range
            if start_date is not None and usage_date < start_date:
                continue
            if end_date is not None and usage_date > end_date:
                continue
            
            # Calculate cost based on energy tariff
            cost = 0.0
            device = devices.get(usage_device_id)
            if device:
                device_home_id = str(device.get("home_id"))
                # Find applicable tariff for this home and date
                applicable_tariff = None
                for tariff in energy_tariffs.values():
                    if str(tariff.get("home_id")) != device_home_id:
                        continue
                    effective_from = tariff.get("effective_from")
                    effective_until = tariff.get("effective_until")
                    # Check if usage_date falls within tariff's effective range
                    if effective_from and usage_date >= effective_from:
                        if effective_until is None or usage_date <= effective_until:
                            applicable_tariff = tariff
                            break
                
                if applicable_tariff:
                    rate = applicable_tariff.get("rate_per_kWh", 0.0)
                    cost = power_consumed * rate
            
            # Create usage record
            record = {
                "usage_id": usage.get("usage_id"),
                "device_id": usage_device_id,
                "usage_date": usage_date,
                "power_consumed_kWh": power_consumed,
                "cost": round(cost, 2),
                "created_at": usage.get("created_at"),
                "consumption_summary": usage.get("consumption_summary")
            }
            
            results.append(record)
            total_consumption += power_consumed
            total_cost += cost
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "total_power_consumed_kWh": round(total_consumption, 2),
            "total_cost": round(total_cost, 2),
            "usage_records": results
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_device_energy_use",
                "description": "Get energy usage data for devices. Can filter by home_id, home_name, device_id, and date range (start_date/end_date). Returns usage records with total power consumption in kWh.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Filter energy usage by home ID (optional)."
                        },
                        "home_name": {
                            "type": "string",
                            "description": "Filter energy usage by home name (optional). Will be used to resolve home_id if provided."
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Filter energy usage by specific device ID (optional)."
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date for filtering usage records in YYYY-MM-DD format (optional). Inclusive."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date for filtering usage records in YYYY-MM-DD format (optional). Inclusive."
                        }
                    },
                    "required": []
                }
            }
        }
