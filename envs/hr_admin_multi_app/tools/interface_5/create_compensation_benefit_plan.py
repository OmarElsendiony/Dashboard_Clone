import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateCompensationBenefitPlan(Tool):
    """Create a new compensation benefit plan entry with validated inputs."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        name: str,
        current_cost: float,
        previous_year_cost: float,
        enrollment_window: str,
        benefit_status: Optional[str] = "active",
    ) -> str:
        """
        Create a benefit plan. Name must be unique, status must be active/inactive, and current_cost must be > 0.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        benefit_plans = data.get("benefit_plans")
        if not isinstance(benefit_plans, dict):
            return json.dumps({"success": False, "error": "benefit_plans store missing"})

        if not isinstance(name, str) or not name.strip():
            return json.dumps({"success": False, "error": "name must be provided"})
        plan_name = name.strip()

        status_value = benefit_status.strip().lower() if isinstance(benefit_status, str) else "active"
        if status_value not in {"active", "inactive"}:
            return json.dumps({"success": False, "error": "benefit_status must be active or inactive"})

        for plan in benefit_plans.values():
            if str(plan.get("name", "")).strip().lower() == plan_name.lower():
                return json.dumps({"success": False, "error": f"Benefit plan '{plan_name}' already exists"})

        try:
            cost_decimal = Decimal(str(current_cost)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            return json.dumps({"success": False, "error": "current_cost must be numeric"})
        if cost_decimal <= 0:
            return json.dumps({"success": False, "error": "current_cost must be greater than 0"})

        try:
            previous_cost_decimal = Decimal(str(previous_year_cost)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            return json.dumps({"success": False, "error": "previous_year_cost must be numeric"})
        if previous_cost_decimal <= 0:
            return json.dumps({"success": False, "error": "previous_year_cost must be greater than 0"})

        if not isinstance(enrollment_window, str) or not enrollment_window.strip():
            return json.dumps({"success": False, "error": "enrollment_window is required"})
        window_value = enrollment_window.strip().lower()
        if window_value not in {"open", "closed"}:
            return json.dumps({"success": False, "error": "enrollment_window must be open or closed"})

        cost_variance = ((cost_decimal - previous_cost_decimal) / previous_cost_decimal * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        plan_id = generate_id(benefit_plans)
        timestamp = "2025-12-12T12:00:00"

        record = {
            "plan_id": plan_id,
            "name": plan_name,
            "status": status_value,
            "current_cost": f"{cost_decimal:.2f}",
            "previous_year_cost": f"{previous_cost_decimal:.2f}",
            "enrollment_window": window_value,
            "cost_variance_percent": f"{cost_variance:.2f}",
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        benefit_plans[plan_id] = record

        return json.dumps(
            {
                "success": True,
                "message": f"Benefit plan '{plan_name}' created",
                "plan": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_compensation_benefit_plan",
                "description": "Create a compensation benefit plan with a unique name, status, and current_cost.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Benefit plan name; must be unique.",
                        },
                        "current_cost": {
                            "type": "number",
                            "description": "Current plan cost; must be greater than 0.",
                        },
                        "previous_year_cost": {
                            "type": "number",
                            "description": "Previous year cost; must be greater than 0.",
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "Enrollment window; allowed values: open or closed.",
                        },
                        "benefit_status": {
                            "type": "string",
                            "description": "Plan status; allowed values: active or inactive.",
                        },
                    },
                    "required": ["name", "current_cost", "previous_year_cost", "enrollment_window"],
                },
            },
        }
