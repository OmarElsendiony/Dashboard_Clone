import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class FetchDeductionCode(Tool):
    """Retrieve deduction code records filtered by type, status, or id."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        deduction_code_type: str,
        status: Optional[str] = None,
        deduction_code_id: Optional[str] = None,
    ) -> str:
        """
        Fetch deduction code matching the provided deduction_type and optional filters.
        """

        def normalize(value: str) -> str:
            return value.strip().lower()

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        deduction_rules = data.get("deduction_rules")
        if not isinstance(deduction_rules, dict):
            return json.dumps({"success": False, "error": "deduction_rules store missing"})

        if not isinstance(deduction_code_type, str) or not deduction_code_type.strip():
            return json.dumps({"success": False, "error": "deduction_code_type must be provided"})

        allowed_types = {
            "benefit_contribution",
            "repayment_of_overpayment",
            "loan",
            "retirement",
            "insurance",
            "tax",
            "garnishment",
        }

        target_type = normalize(deduction_code_type)
        if target_type not in allowed_types:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        "deduction_code_type must be one of "
                        "benefit_contribution, repayment_of_overpayment, loan, retirement, insurance, tax, garnishment"
                    ),
                }
            )
        status_filter = normalize(status) if status else None
        if status_filter and status_filter not in {"active", "inactive"}:
            return json.dumps({"success": False, "error": "status must be active or inactive"})

        rule_id_filter = deduction_code_id.strip() if isinstance(deduction_code_id, str) and deduction_code_id.strip() else None

        results = []
        for rule_id, rule in deduction_rules.items():
            if rule_id_filter and rule_id != rule_id_filter:
                continue
            if normalize(rule.get("deduction_type", "")) != target_type:
                continue
            if status_filter and normalize(rule.get("status", "")) != status_filter:
                continue
            record = dict(rule)
            record["deduction_code_id"] = rule_id
            record["deduction_code_type"] = record.get("deduction_type")
            results.append(record)

        if not results:
            return json.dumps({"success": False, "error": "No deduction rules found matching criteria"})

        return json.dumps({"success": True, "count": len(results), "deduction_codes": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_deduction_code",
                "description": "Retrieve deduction rules filtered by type, status, id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deduction_code_type": {
                            "type": "string",
                            "description": "Deduction type to search for (benefit_contribution, repayment_of_overpayment, loan, retirement, insurance, tax, garnishment).",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter; allowed values: active or inactive.",
                        },
                        "deduction_code_id": {
                            "type": "string",
                            "description": "Optional specific rule identifier to fetch exactly one record.",
                        },
                    },
                    "required": ["deduction_code_type"],
                },
            },
        }
