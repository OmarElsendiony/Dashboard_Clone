import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class UpdateEmployeeBenefitPlan(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        plan_id: str,
        updates: Dict[str, Any],
    ) -> str:
        """
        Update an existing benefit plan.
        
        Args:
            data: The database dictionary containing all tables.
            plan_id: The ID of the benefit plan to update (required).
            updates: JSON object containing fields to update (required).
                Supported fields: name, current_cost, previous_year_cost, enrollment_window, status.
                enrollment_window allowed values: 'open', 'closed'.
                status allowed values: 'active', 'inactive'.
        
        Returns:
            JSON string with the updated benefit plan record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not plan_id:
            return json.dumps({"error": "Missing required parameter: plan_id is required"})
        if not updates or not isinstance(updates, dict):
            return json.dumps({"error": "Missing required parameter: updates must be a JSON object"})

        plan_id = str(plan_id)
        benefit_plans = data.get("benefit_plans", {})

        if plan_id not in benefit_plans:
            return json.dumps({"error": f"Benefit plan with ID '{plan_id}' not found"})

        plan = benefit_plans[plan_id]

        # Validate status if being updated
        if "status" in updates:
            allowed_statuses = ["active", "inactive"]
            if updates["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
                })

        # Validate enrollment_window if being updated
        if "enrollment_window" in updates:
            allowed_windows = ["open", "closed"]
            if updates["enrollment_window"] not in allowed_windows:
                return json.dumps({
                    "error": f"Invalid enrollment_window. Allowed values: {', '.join(allowed_windows)}"
                })

        # Validate name uniqueness if being updated
        if "name" in updates:
            for p_id, p in benefit_plans.items():
                if p_id != plan_id and p.get("name") == updates["name"]:
                    return json.dumps({"error": f"Benefit plan with name '{updates['name']}' already exists"})

        # Allowed fields to update
        allowed_fields = ["name", "current_cost", "previous_year_cost", "enrollment_window", "status"]

        for key, value in updates.items():
            if key in allowed_fields:
                plan[key] = value

        # Recalculate cost variance if costs changed
        current_cost = plan.get("current_cost")
        previous_year_cost = plan.get("previous_year_cost")
        if current_cost is not None and previous_year_cost is not None and previous_year_cost != 0:
            plan["cost_variance_percent"] = ((float(current_cost) - float(previous_year_cost)) / float(previous_year_cost)) * 100

        plan["last_updated"] = "2025-11-16T23:59:00"

        return json.dumps(plan)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_employee_benefit_plan",
                "description": (
                    "Updates an existing benefit plan with the provided fields. "
                    "Automatically recalculates cost variance if costs are updated."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                            "description": "The ID of the benefit plan to update (required).",
                        },
                        "updates": {
                            "type": "object",
                            "description": (
                                "JSON object containing fields to update (required). "
                                "Supported fields: name, current_cost, previous_year_cost, enrollment_window, status."
                            ),
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "The name of the benefit plan.",
                                },
                                "current_cost": {
                                    "type": "number",
                                    "description": "The current cost of the plan.",
                                },
                                "previous_year_cost": {
                                    "type": "number",
                                    "description": "The previous year cost of the plan.",
                                },
                                "enrollment_window": {
                                    "type": "string",
                                    "description": "The enrollment window status. Allowed values: 'open', 'closed'.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The plan status. Allowed values: 'active', 'inactive'.",
                                },
                            },
                        },
                    },
                    "required": ["plan_id", "updates"],
                },
            },
        }
