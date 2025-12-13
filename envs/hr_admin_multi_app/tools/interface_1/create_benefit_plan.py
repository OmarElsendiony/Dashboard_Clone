import json
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateBenefitPlan(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        name: str,
        current_cost: float,
        previous_year_cost: float,
        enrollment_window: str,
        status: str = "active",
    ) -> str:
        """Create a benefit plan record."""

        def ensure_decimal(value: Any, field: str) -> Decimal:
            try:
                dec_value = Decimal(str(value))
            except (InvalidOperation, TypeError):
                raise ValueError(f"{field} must be a numeric value")
            if dec_value < 0:
                raise ValueError(f"{field} must be zero or greater")
            return dec_value.quantize(Decimal("0.1"))

        def generate_plan_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            numeric_ids = []
            for key in table.keys():
                try:
                    numeric_ids.append(int(key))
                except (TypeError, ValueError):
                    continue
            next_id = max(numeric_ids, default=0) + 1
            return str(next_id)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        benefit_plans = data.setdefault("benefit_plans", {})
        if not isinstance(benefit_plans, dict):
            return json.dumps({"success": False, "error": "Invalid benefit_plans structure"})

        if not isinstance(name, str) or not name.strip():
            return json.dumps({"success": False, "error": "name must be a non-empty string"})
        plan_name = name.strip()

        if not isinstance(enrollment_window, str) or enrollment_window not in {"open", "closed"}:
            return json.dumps({"success": False, "error": "enrollment_window must be 'open' or 'closed'"})

        if not isinstance(status, str) or status not in {"active", "inactive"}:
            return json.dumps({"success": False, "error": "status must be 'active' or 'inactive'"})

        try:
            current_dec = ensure_decimal(current_cost, "current_cost")
            previous_dec = ensure_decimal(previous_year_cost, "previous_year_cost")
        except ValueError as exc:
            return json.dumps({"success": False, "error": str(exc)})

        plan_id = generate_plan_id(benefit_plans)

        # Ensure plan name uniqueness (case-insensitive, trimmed)
        for existing_id, existing in benefit_plans.items():
            if not isinstance(existing, dict):
                continue
            existing_name = (existing.get("name") or "").strip().lower()
            if existing_name == plan_name.lower():
                return json.dumps({"success": False, "error": f"Benefit plan with name '{name}' already exists"})

        timestamp = "2025-11-22T12:00:00"
        record = {
            "plan_id": plan_id,
            "name": plan_name,
            "status": status,
            "current_cost": float(current_dec),
            "previous_year_cost": float(previous_dec),
            "enrollment_window": enrollment_window,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        # Calculate cost variance if previous cost is positive
        if float(previous_dec) > 0:
            variance = ((float(current_dec) - float(previous_dec)) / float(previous_dec)) * 100
            record["cost_variance_percent"] = round(variance, 2)

        benefit_plans[plan_id] = record

        return json.dumps({
            "success": True,
            "message": "Benefit plan created",
            "benefit_plan": record,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_benefit_plan",
                "description": "Create a benefit plan matching the benefit_plans schema (name, status, costs, window).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Benefit plan name."},
                        "current_cost": {"type": "number", "description": "Current plan cost as a non-negative decimal."},
                        "previous_year_cost": {"type": "number", "description": "Previous year plan cost as a non-negative decimal."},
                        "enrollment_window": {"type": "string", "description": "Enrollment window (allowed values: open, closed)."},
                        "status": {"type": "string", "description": "Lifecycle status (allowed values: active, inactive).", "default": "active"},
                    },
                    "required": ["name", "current_cost", "previous_year_cost", "enrollment_window"],
                },
            },
        }
