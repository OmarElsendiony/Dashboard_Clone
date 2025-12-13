import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateDeductionCode(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        deduction_code_type: str,
        max_percent_net_pay: float,
        status: Optional[str] = "active",
    ) -> str:
        """Create a deduction code (ADP terminology) which maps to a deduction rule."""

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        deduction_rules = data.get("deduction_rules")
        if not isinstance(deduction_rules, dict):
            return json.dumps({"success": False, "error": "deduction_rules store missing"})

        if not isinstance(deduction_code_type, str) or not deduction_code_type.strip():
            return json.dumps({"success": False, "error": "deduction_code_type must be provided"})
        code_type_clean = deduction_code_type.strip()

        allowed_types = {
            "benefit_contribution",
            "repayment_of_overpayment",
            "loan",
            "retirement",
            "insurance",
            "tax",
            "garnishment",
        }
        if code_type_clean.lower() not in allowed_types:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        "deduction_code_type must be one of "
                        "benefit_contribution, repayment_of_overpayment, loan, retirement, insurance, tax, garnishment"
                    ),
                }
            )

        try:
            percent_decimal = Decimal(str(max_percent_net_pay)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            return json.dumps({"success": False, "error": "max_percent_net_pay must be numeric"})
        if percent_decimal <= 0 or percent_decimal > 1:
            return json.dumps({"success": False, "error": "max_percent_net_pay must be between 0 and 1"})

        status_value = status.strip().lower() if isinstance(status, str) else "active"
        if status_value not in {"active", "inactive"}:
            return json.dumps({"success": False, "error": "status must be active or inactive"})

        for rule in deduction_rules.values():
            if not isinstance(rule, dict):
                continue
            existing_type = normalize(rule.get("deduction_type"))
            existing_percent = normalize(rule.get("max_percent_of_net_pay"))
            existing_status = normalize(rule.get("status"))
            if (
                existing_type == code_type_clean.lower()
                and existing_percent == f"{percent_decimal:.2f}"
                and existing_status == status_value
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Deduction code with the same type, max_percent_net_pay, and status already exists",
                    }
                )

        deduction_code_id = generate_id(deduction_rules)
        timestamp = "2025-12-12T12:00:00"

        record = {
            "rule_id": deduction_code_id,
            "deduction_type": code_type_clean,
            "max_percent_of_net_pay": f"{percent_decimal:.2f}",
            "status": status_value,
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        deduction_rules[deduction_code_id] = record

        api_payload = dict(record)
        api_payload["deduction_code_id"] = deduction_code_id
        api_payload["deduction_code_type"] = record["deduction_type"]

        return json.dumps(
            {
                "success": True,
                "message": f"Deduction code '{deduction_code_type}' created",
                "deduction_code": api_payload,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_deduction_code",
                "description": "Create a deduction code with type, percent limit, and status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deduction_code_type": {
                            "type": "string",
                            "description": (
                                "Deduction code type. Allowed values: "
                                "benefit_contribution, repayment_of_overpayment, loan, retirement, insurance, tax, garnishment."
                            ),
                        },
                        "max_percent_net_pay": {
                            "type": "number",
                            "description": "Required percent cap between 0 and 1.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional code status; allowed values: active or inactive, default: active.",
                        },
                    },
                    "required": ["deduction_code_type", "max_percent_net_pay"],
                },
            },
        }
