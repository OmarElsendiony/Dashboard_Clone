import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class AddBenefitPlan(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        name: str,
        current_cost: float,
        previous_year_cost: float,
        enrollment_window: str = "open",
        status: str = "active",
    ) -> str:
        """
        Create a new benefit plan.
        
        Args:
            data: The database dictionary containing all tables.
            name: The name of the benefit plan (required).
            current_cost: The current cost of the plan (required).
            previous_year_cost: The previous year cost of the plan (required).
            enrollment_window: The enrollment window status. Allowed values: 'open', 'closed'. Defaults to 'closed'.
            status: The plan status. Allowed values: 'active', 'inactive'. Defaults to 'active'.
        
        Returns:
            JSON string with the created benefit plan record.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            max_id = 0
            for k in table.keys():
                try:
                    max_id = max(max_id, int(k))
                except ValueError:
                    continue
            return str(max_id + 1)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not name:
            return json.dumps({"error": "Missing required parameter: name is required"})
        if current_cost is None:
            return json.dumps({"error": "Missing required parameter: current_cost is required"})
        if previous_year_cost is None:
            return json.dumps({"error": "Missing required parameter: previous_year_cost is required"})

        # Validate status
        allowed_statuses = ["active", "inactive"]
        if status not in allowed_statuses:
            return json.dumps({
                "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
            })

        # Validate enrollment_window
        allowed_windows = ["open", "closed"]
        if enrollment_window not in allowed_windows:
            return json.dumps({
                "error": f"Invalid enrollment_window. Allowed values: {', '.join(allowed_windows)}"
            })

        benefit_plans = data.get("benefit_plans", {})

        # Check for duplicate name
        for plan_id, plan in benefit_plans.items():
            if plan.get("name") == name:
                return json.dumps({"error": f"Benefit plan with name '{name}' already exists"})

        # Calculate cost variance percent
        cost_variance_percent = None
        if previous_year_cost and previous_year_cost != 0:
            cost_variance_percent = ((float(current_cost) - float(previous_year_cost)) / float(previous_year_cost)) * 100

        # Generate new plan ID
        plan_id = generate_id(benefit_plans)

        # Create benefit plan record
        timestamp = "2025-12-12T12:00:00"
        new_plan = {
            "plan_id": plan_id,
            "name": name,
            "status": status,
            "current_cost": float(current_cost),
            "previous_year_cost": float(previous_year_cost),
            "enrollment_window": enrollment_window,
            "cost_variance_percent": cost_variance_percent,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        benefit_plans[plan_id] = new_plan
        data["benefit_plans"] = benefit_plans

        return json.dumps(new_plan)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_benefit_plan",
                "description": (
                    "Creates a new benefit plan in the system. "
                    "Automatically calculates the cost variance percentage."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the benefit plan (required).",
                        },
                        "current_cost": {
                            "type": "number",
                            "description": "The current cost of the plan (required).",
                        },
                        "previous_year_cost": {
                            "type": "number",
                            "description": "The previous year cost of the plan (required).",
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "The enrollment window status. Allowed values: 'open', 'closed'. Defaults to 'closed'.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The plan status. Allowed values: 'active', 'inactive'. Defaults to 'active'.",
                        },
                    },
                    "required": ["name", "current_cost", "previous_year_cost"],
                },
            },
        }
