import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class ListBenefitPlans(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        List all benefit plans with optional filters.
        
        Args:
            data: The database dictionary containing all tables.
            filters: Optional JSON object with filter key-value pairs (AND logic).
                Supported fields: plan_id, name, status, enrollment_window.
                status allowed values: 'active', 'inactive'.
                enrollment_window allowed values: 'open', 'closed'.
        
        Returns:
            JSON string with entity_type, count, and results array.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if filters is not None and not isinstance(filters, dict):
            return json.dumps({"error": "filters must be a JSON object if provided"})

        # Access benefit_plans table
        benefit_plans = data.get("benefit_plans", {})
        results = []
        effective_filters = filters or {}

        # Validate status filter if provided
        if "status" in effective_filters:
            allowed_statuses = ["active", "inactive"]
            if effective_filters["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status filter. Allowed values: {', '.join(allowed_statuses)}"
                })

        # Validate enrollment_window filter if provided
        if "enrollment_window" in effective_filters:
            allowed_windows = ["open", "closed"]
            if effective_filters["enrollment_window"] not in allowed_windows:
                return json.dumps({
                    "error": f"Invalid enrollment_window filter. Allowed values: {', '.join(allowed_windows)}"
                })

        for record_id, record in benefit_plans.items():
            if not isinstance(record, dict):
                continue

            match = True
            for key, value in effective_filters.items():
                if key == "plan_id":
                    stored_id = record.get("plan_id")
                    if str(record_id) != str(value) and str(stored_id) != str(value):
                        match = False
                        break
                else:
                    if record.get(key) != value:
                        match = False
                        break

            if match:
                result_record = {
                    "plan_id": record.get("plan_id", str(record_id)),
                    "name": record.get("name"),
                    "status": record.get("status"),
                    "current_cost": record.get("current_cost"),
                    "previous_year_cost": record.get("previous_year_cost"),
                    "enrollment_window": record.get("enrollment_window"),
                    "cost_variance_percent": record.get("cost_variance_percent"),
                    "created_at": record.get("created_at"),
                    "last_updated": record.get("last_updated"),
                }
                results.append(result_record)

        return json.dumps({
            "entity_type": "benefit_plans",
            "count": len(results),
            "results": results,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_benefit_plans",
                "description": (
                    "Lists all benefit plans available in the system. "
                    "Optional filters allow narrowing results by plan attributes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": (
                                "Optional JSON object with filter key-value pairs (AND logic). "
                                "Supported fields: plan_id, name, status, enrollment_window."
                            ),
                            "properties": {
                                "plan_id": {
                                    "type": "string",
                                    "description": "The unique identifier of the benefit plan.",
                                },
                                "name": {
                                    "type": "string",
                                    "description": "The name of the benefit plan.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The plan status. Allowed values: 'active', 'inactive'.",
                                },
                                "enrollment_window": {
                                    "type": "string",
                                    "description": "The enrollment window status. Allowed values: 'open', 'closed'.",
                                },
                            },
                        },
                    },
                    "required": [],
                },
            },
        }
