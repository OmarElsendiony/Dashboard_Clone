import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateBenefitPlan(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        plan_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        current_cost: Optional[float] = None,
        previous_year_cost: Optional[float] = None,
        enrollment_window: Optional[str] = None,
    ) -> str:
        """
        Update benefit plan records in the HR system.

        Args:
            data: Environment data containing benefit_plans
            plan_id: The benefit plan identifier (required)
            name: Updated plan name (optional)
            status: Plan status - 'active', 'inactive' (optional)
            current_cost: Updated current year cost (optional)
            previous_year_cost: Updated previous year cost (optional)
            enrollment_window: Enrollment window status - 'open', 'closed' (optional)
        """
        timestamp = "2025-11-16T23:59:00"
        benefit_plans = data.get("benefit_plans", {})

        # Validate required parameter
        if not plan_id:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: plan_id"}
            )

        # Validate that benefit plan exists
        if plan_id not in benefit_plans:
            return json.dumps(
                {"success": False, "error": f"Halt: Benefit plan not found"}
            )

        # Validate at least one optional field is provided
        if all(
            param is None
            for param in [
                name,
                status,
                current_cost,
                previous_year_cost,
                enrollment_window,
            ]
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one optional parameter (name, status, current_cost, previous_year_cost, enrollment_window) must be provided for updates",
                }
            )

        # Get current benefit plan
        current_plan = benefit_plans[plan_id]

        # Validate status if provided
        if status is not None:
            valid_statuses = ["active", "inactive"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Halt: Benefit plan operation failed - status must be one of: {', '.join(valid_statuses)}",
                    }
                )

        # Validate enrollment_window if provided
        if enrollment_window is not None:
            valid_windows = ["open", "closed"]
            if enrollment_window not in valid_windows:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Halt: Benefit plan operation failed - enrollment_window must be one of: {', '.join(valid_windows)}",
                    }
                )

        # Validate cost values if provided
        if current_cost is not None:
            try:
                current_cost = float(current_cost)
                if current_cost < 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Halt: Benefit plan operation failed - current_cost must be non-negative",
                        }
                    )
            except (ValueError, TypeError):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Halt: Benefit plan operation failed - invalid current_cost format",
                    }
                )

        if previous_year_cost is not None:
            try:
                previous_year_cost = float(previous_year_cost)
                if previous_year_cost < 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Halt: Benefit plan operation failed - previous_year_cost must be non-negative",
                        }
                    )
            except (ValueError, TypeError):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Halt: Benefit plan operation failed - invalid previous_year_cost format",
                    }
                )

        # Validate name uniqueness if being updated
        if name is not None:
            for existing_plan_id, existing_plan in benefit_plans.items():
                if existing_plan_id != plan_id and existing_plan.get("name") == name:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Halt: Benefit plan with name '{name}' already exists",
                        }
                    )

        # Update benefit plan record
        updated_plan = current_plan.copy()

        if name is not None:
            updated_plan["name"] = name

        if status is not None:
            updated_plan["status"] = status

        if current_cost is not None:
            updated_plan["current_cost"] = current_cost

        if previous_year_cost is not None:
            updated_plan["previous_year_cost"] = previous_year_cost

        if enrollment_window is not None:
            updated_plan["enrollment_window"] = enrollment_window

        # Recalculate cost_variance_percent if costs are updated
        final_current_cost = updated_plan.get("current_cost")
        final_previous_cost = updated_plan.get("previous_year_cost")

        if (
            final_current_cost is not None
            and final_previous_cost is not None
            and final_previous_cost > 0
        ):
            cost_variance = (
                (final_current_cost - final_previous_cost) / final_previous_cost
            ) * 100
            updated_plan["cost_variance_percent"] = round(cost_variance, 2)

        updated_plan["last_updated"] = timestamp
        benefit_plans[plan_id] = updated_plan

        return json.dumps(updated_plan)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_benefit_plan",
                "description": "Update benefit plan records in the HR benefits system. This tool modifies existing benefit plans while maintaining data integrity and business rules. Allows updates to plan name, status, cost information, and enrollment windows. Validates status values ('active', 'inactive'), enrollment window states ('open', 'closed'), ensures cost values are non-negative, and prevents duplicate plan names. Automatically recalculates cost variance percentage when cost values are updated using the formula: ((current_cost - previous_year_cost) / previous_year_cost) * 100. Essential for benefits administration, annual benefit plan updates, cost adjustments, and enrollment period management.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                            "description": "Benefit plan identifier (required, must exist in system)",
                        },
                        "name": {
                            "type": "string",
                            "description": "Updated plan name (optional, must be unique)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Plan status: 'active', 'inactive' (optional)",
                        },
                        "current_cost": {
                            "type": "number",
                            "description": "Updated current year cost (optional, must be non-negative)",
                        },
                        "previous_year_cost": {
                            "type": "number",
                            "description": "Updated previous year cost (optional, must be non-negative)",
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "Enrollment window status: 'open', 'closed' (optional)",
                        },
                    },
                    "required": ["plan_id"],
                },
            },
        }
