import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class UpdateCompensationBenefitPlan(Tool):
    """Update an existing compensation benefit plan identified by benefit_name (and optional plan_id)."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        benefit_name: str,
        plan_id: Optional[str] = None,
        new_name: Optional[str] = None,
        current_cost: Optional[float] = None,
        previous_year_cost: Optional[float] = None,
        enrollment_window: Optional[str] = None,
        benefit_status: Optional[str] = None,
    ) -> str:
        """
        Update any combination of plan attributes. At least one updatable field must be provided.
        """

        def normalize(value: str) -> str:
            return value.strip().lower()

        def to_decimal(value: float, field: str) -> Decimal:
            try:
                dec = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except (InvalidOperation, ValueError):
                raise ValueError(f"{field} must be numeric")
            if dec <= 0:
                raise ValueError(f"{field} must be greater than 0")
            return dec

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        benefit_plans = data.get("benefit_plans")
        if not isinstance(benefit_plans, dict):
            return json.dumps({"success": False, "error": "benefit_plans store missing"})

        if not isinstance(benefit_name, str) or not benefit_name.strip():
            return json.dumps({"success": False, "error": "benefit_name must be provided"})

        target_name = normalize(benefit_name)
        target_plan_id = plan_id.strip() if isinstance(plan_id, str) and plan_id.strip() else None

        found_plan_id = None
        plan = None
        for pid, record in benefit_plans.items():
            if normalize(record.get("name", "")) == target_name:
                if target_plan_id and pid != target_plan_id:
                    continue
                found_plan_id = pid
                plan = record
                break

        if not plan:
            return json.dumps({"success": False, "error": f"Benefit plan '{benefit_name}' not found"})

        if target_plan_id and found_plan_id != target_plan_id:
            return json.dumps({"success": False, "error": f"Benefit plan id '{target_plan_id}' not found"})

        updates = False

        if new_name:
            new_name_clean = new_name.strip()
            if not new_name_clean:
                return json.dumps({"success": False, "error": "new_name cannot be empty"})
            for pid, record in benefit_plans.items():
                if pid == found_plan_id:
                    continue
                if normalize(record.get("name", "")) == normalize(new_name_clean):
                    return json.dumps({"success": False, "error": f"Benefit plan '{new_name_clean}' already exists"})
            plan["name"] = new_name_clean
            updates = True

        if current_cost is not None:
            try:
                cost_decimal = to_decimal(current_cost, "current_cost")
            except ValueError as exc:
                return json.dumps({"success": False, "error": str(exc)})
            plan["current_cost"] = f"{cost_decimal:.2f}"
            updates = True
        else:
            cost_decimal = Decimal(plan.get("current_cost", "0") or "0").quantize(Decimal("0.01"))

        if previous_year_cost is not None:
            try:
                prev_decimal = to_decimal(previous_year_cost, "previous_year_cost")
            except ValueError as exc:
                return json.dumps({"success": False, "error": str(exc)})
            plan["previous_year_cost"] = f"{prev_decimal:.2f}"
            updates = True
        else:
            prev_decimal = Decimal(plan.get("previous_year_cost", "0") or "0").quantize(Decimal("0.01")) or cost_decimal
            if prev_decimal <= 0:
                prev_decimal = cost_decimal

        if enrollment_window is not None:
            if not enrollment_window.strip():
                return json.dumps({"success": False, "error": "enrollment_window cannot be empty"})
            window_value = enrollment_window.strip().lower()
            if window_value not in {"open", "closed"}:
                return json.dumps({"success": False, "error": "enrollment_window must be open or closed"})
            plan["enrollment_window"] = window_value
            updates = True

        if benefit_status is not None:
            status_value = benefit_status.strip().lower()
            if status_value not in {"active", "inactive"}:
                return json.dumps({"success": False, "error": "benefit_status must be active or inactive"})
            plan["status"] = status_value
            updates = True

        if not updates:
            return json.dumps({"success": False, "error": "No updates provided"})

        if prev_decimal > 0:
            variance = ((cost_decimal - prev_decimal) / prev_decimal * Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            variance = Decimal("0.00")
        plan["cost_variance_percent"] = f"{variance:.2f}"
        plan["last_updated"] = "2025-12-12T12:00:00"

        return json.dumps({"success": True, "plan": plan})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_compensation_benefit_plan",
                "description": "Update an existing benefit plan identified by benefit_name and optional plan_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "benefit_name": {"type": "string", "description": "Name of the benefit plan to update."},
                        "plan_id": {"type": "string", "description": "Optional plan id."},
                        "new_name": {"type": "string", "description": "Optional new plan name; must remain unique."},
                        "current_cost": {"type": "number", "description": "Optional updated current cost > 0."},
                        "previous_year_cost": {"type": "number", "description": "Optional updated previous year cost > 0."},
                        "enrollment_window": {
                            "type": "string",
                            "description": "Optional updated enrollment window; allowed values: open or closed.",
                        },
                        "benefit_status": {
                            "type": "string",
                            "description": "Optional updated status; allowed values: active or inactive.",
                        },
                    },
                    "required": ["benefit_name"],
                },
            },
        }
