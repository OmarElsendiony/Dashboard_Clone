import json
from typing import Any, Dict, List, Optional

from tau_bench.envs.tool import Tool


class GetBenefitData(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        plan_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Fetch benefit plans with plan id and filters.

        Input:
        - plan_id: optional
        - filters: object with any of {name, enrollment_window, status}
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: data must be a dict"})

        plans_dict: Dict[str, Dict[str, Any]] = data.get("benefit_plans", {}) or {}
        if not isinstance(plans_dict, dict):
            return json.dumps({"success": False, "error": "Invalid container: data['benefit_plans'] must be a dict"})

        if plan_id is not None and not isinstance(plan_id, str):
            return json.dumps({"success": False, "error": "Invalid plan_id: must be a string"})

        # filters strict validation
        filters = filters or {}
        if not isinstance(filters, dict):
            return json.dumps({"success": False, "error": "Invalid filters: must be an object"})
        allowed_keys = {"name", "enrollment_window", "status"}
        unknown_keys = [k for k in filters.keys() if k not in allowed_keys]
        if unknown_keys:
            msg = "Invalid filter keys: " + ", ".join(sorted(unknown_keys)) + ". Allowed: " + ", ".join(sorted(allowed_keys))
            return json.dumps({"success": False, "error": msg})
        active = {}
        for k, v in filters.items():
            if v is None:
                continue
            if not isinstance(v, str):
                return json.dumps({"success": False, "error": "Invalid type for '" + k + "': must be string"})
            active[k] = v

        valid_enrollment_window = {"open", "closed"}
        valid_status = {"active", "inactive"}
        if "enrollment_window" in active and active["enrollment_window"] not in valid_enrollment_window:
            return json.dumps({"success": False, "error": "Invalid value for 'enrollment_window'"})
        if "status" in active and active["status"] not in valid_status:
            return json.dumps({"success": False, "error": "Invalid value for 'status'"})

        results: List[Dict[str, Any]] = []
        for plan in plans_dict.values():
            if not isinstance(plan, dict):
                continue

            # Apply filters
            if plan_id is not None and plan.get("plan_id") != plan_id:
                continue
            if "name" in active:
                if (plan.get("name") or "").lower() != str(active["name"]).lower():
                    continue
            if "enrollment_window" in active and plan.get("enrollment_window") != active["enrollment_window"]:
                continue
            if "status" in active and plan.get("status") != active["status"]:
                continue

            results.append(plan.copy())

        return json.dumps({
            "success": True,
            "benefit_plans": results,
            "count": len(results),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_benefit_data",
                "description": "Fetch benefit plans using plan_id and several filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_id": {"type": "string", "description": "Benefit plan id to fetch."},
                        "filters": {
                            "type": "object",
                            "description": "Optional filters supporting name, enrollment_window, and status.",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the plan."},
                                "enrollment_window": {"type": "string", "description": "Enrollment window filter (allowed values: open, closed)."},
                                "status": {"type": "string", "description": "Lifecycle status filter (allowed values: active, inactive)."}
                            }
                        }
                    },
                    "required": []
                }
            },
        }
