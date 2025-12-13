import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CollectBenefitPlanDetails(Tool):
    """Fetch details for a benefit plan identified by its unique name and optional filters."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        benefit_name: str,
        status: str = "active",
        plan_id: Optional[str] = None,
        enrollment_window: Optional[str] = None,
    ) -> str:
        """
        Return the benefit plan record that matches benefit_name.
        """

        def normalize(value: str) -> str:
            return value.strip().lower()

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        benefit_plans = data.get("benefit_plans")
        if not isinstance(benefit_plans, dict):
            return json.dumps({"success": False, "error": "benefit_plans store missing"})

        if not isinstance(benefit_name, str) or not benefit_name.strip():
            return json.dumps({"success": False, "error": "benefit_name must be provided"})

        allowed_statuses = {"active", "inactive"}
        normalized_status = normalize(status) if status else None
        if normalized_status and normalized_status not in allowed_statuses:
            return json.dumps({"success": False, "error": "status must be active or inactive"})

        allowed_windows = {"open", "closed"}
        normalized_window = normalize(enrollment_window) if enrollment_window else None
        if normalized_window and normalized_window not in allowed_windows:
            return json.dumps({"success": False, "error": "enrollment_window must be open or closed"})

        target_name = normalize(benefit_name)
        target_plan_id = plan_id.strip() if isinstance(plan_id, str) and plan_id.strip() else None

        if target_plan_id:
            plan = benefit_plans.get(target_plan_id)
            if not plan:
                return json.dumps({"success": False, "error": f"Benefit plan id '{target_plan_id}' not found"})
            if normalize(plan.get("name", "")) != target_name:
                return json.dumps({"success": False, "error": "benefit_name and plan_id refer to different plans"})
            if normalized_status and normalize(plan.get("status")) != normalized_status:
                return json.dumps({"success": False, "error": "Plan found but status mismatch"})
            if normalized_window and normalize(plan.get("enrollment_window")) != normalized_window:
                return json.dumps({"success": False, "error": "Plan found but enrollment_window mismatch"})
            result = dict(plan)
            result["plan_id"] = target_plan_id
            return json.dumps({"success": True, "plan": result})

        for plan_id, plan in benefit_plans.items():
            if normalize(plan.get("name", "")) != target_name:
                continue
            if normalized_status and normalize(plan.get("status")) != normalized_status:
                continue
            if normalized_window and normalize(plan.get("enrollment_window")) != normalized_window:
                continue
            result = dict(plan)
            result["plan_id"] = plan_id
            return json.dumps({"success": True, "plan": result})

        return json.dumps({"success": False, "error": f"Benefit plan '{benefit_name}' not found"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "collect_benefit_plan_details",
                "description": "Retrieve benefit plan details by plan name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "benefit_name": {
                            "type": "string",
                            "description": "Exact benefit plan name to look up.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional plan status filter; allowed values: active, inactive.",
                        },
                        "plan_id": {
                            "type": "string",
                            "description": "Optional plan identifier; when provided it must correspond to benefit_name.",
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "Optional enrollment window filter; allowed values: open, closed.",
                        },
                    },
                    "required": ["benefit_name"],
                },
            },
        }
