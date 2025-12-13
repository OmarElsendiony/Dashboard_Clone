import json
from typing import Any, Dict, List, Optional

from tau_bench.envs.tool import Tool


class GetDeductionRule(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        rule_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Fetch deduction rule records with optional filters."""

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        deduction_rules = data.get("deduction_rules", {})
        if not isinstance(deduction_rules, dict):
            return json.dumps({"success": False, "error": "Invalid deduction_rules structure"})

        if rule_id is not None:
            if not isinstance(rule_id, str) or not rule_id.strip():
                return json.dumps({"success": False, "error": "rule_id must be a non-empty string"})
            rule_id = rule_id.strip()
        if filters is None:
            filters = {}
        if not isinstance(filters, dict):
            return json.dumps({"success": False, "error": "Invalid filters: must be an object"})

        allowed_keys = {"deduction_type", "max_percent_of_net_pay"}
        unknown = [k for k in filters.keys() if k not in allowed_keys]
        if unknown:
            return json.dumps({
                "success": False,
                "error": f"Invalid filter keys: {', '.join(sorted(unknown))}. Allowed: {', '.join(sorted(allowed_keys))}"
            })

        valid_deduction_types = {
            "benefit_contribution",
            "repayment_of_overpayment",
            "loan",
            "retirement",
            "insurance",
            "tax",
            "garnishment",
        }

        active_filters: Dict[str, Any] = {}
        for key, value in filters.items():
            if value is None:
                continue
            if key == "deduction_type":
                if value not in valid_deduction_types:
                    return json.dumps({"success": False, "error": "Invalid deduction_type filter"})
                active_filters[key] = value
            elif key == "max_percent_of_net_pay":
                if not isinstance(value, (int, float)) or value < 0:
                    return json.dumps({"success": False, "error": "max_percent_of_net_pay filter must be non-negative number"})
                active_filters[key] = round(float(value), 4)

        results: List[Dict[str, Any]] = []
        for rule in deduction_rules.values():
            if not isinstance(rule, dict):
                continue
            if rule_id is not None and rule.get("rule_id") != rule_id:
                continue
            match = True
            for key, value in active_filters.items():
                if key == "max_percent_of_net_pay":
                    candidate = rule.get(key)
                    try:
                        candidate_value = round(float(candidate), 4)
                    except (TypeError, ValueError):
                        match = False
                        break
                    if candidate_value != value:
                        match = False
                        break
                elif rule.get(key) != value:
                    match = False
                    break
            if match:
                results.append(rule.copy())

        return json.dumps({
            "success": True,
            "deduction_rules": results,
            "count": len(results),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_deduction_rule",
                "description": "Retrieve deduction rule records with optional filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rule_id": {
                            "type": "string",
                            "description": "(Optional) Exact id of the deduction rule to fetch."
                        },
                        "filters": {
                            "type": "object",
                            "description": "(Optional) Filter object supporting deduction_type and max_percent_of_net_pay.",
                            "properties": {
                                "deduction_type": {
                                    "type": "string",
                                    "description": "Deduction category (allowed values: benefit_contribution, repayment_of_overpayment, loan, retirement, insurance, tax, garnishment).",
                                },
                                "max_percent_of_net_pay": {
                                    "type": "number",
                                    "description": "Filter by max_percent_of_net_pay using a non-negative decimal."
                                },
                            }
                        }
                    },
                    "required": []
                }
            }
        }

