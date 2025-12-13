import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class AssignDeductionToEmployee(Tool):
    """Assign a payroll deduction to an employee for a specific cycle and rule."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        deduction_rule_id: str,
        cycle_id: str,
        amount: float,
        deduction_date: str,
        status: Optional[str] = None,
    ) -> str:
        """
        Create a deduction record. Amount must be > 0, deduction_date must be YYYY-MM-DD.
        Status defaults to 'valid'.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        def validate_date(date_str: str) -> bool:
            try:
                year, month, day = map(int, date_str.split("-"))
            except ValueError:
                return False
            return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        employees = data.get("employees")
        deduction_rules = data.get("deduction_rules")
        payroll_cycles = data.get("payroll_cycles")
        deductions = data.get("deductions")

        if not all(isinstance(store, dict) for store in [employees, deduction_rules, payroll_cycles, deductions]):
            return json.dumps({"success": False, "error": "Missing employees, deduction_rules, payroll_cycles, or deductions store"})

        employee = employees.get(employee_id)
        if not employee:
            return json.dumps({"success": False, "error": f"Employee '{employee_id}' not found"})

        rule = deduction_rules.get(deduction_rule_id)
        if not rule:
            return json.dumps({"success": False, "error": f"Deduction rule '{deduction_rule_id}' not found"})
        if str(rule.get("status", "")).strip().lower() != "active":
            return json.dumps({"success": False, "error": "Deduction rule must be active"})

        cycle = payroll_cycles.get(cycle_id)
        if not cycle:
            return json.dumps({"success": False, "error": f"Payroll cycle '{cycle_id}' not found"})

        try:
            amount_decimal = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            return json.dumps({"success": False, "error": "amount must be numeric"})
        if amount_decimal <= 0:
            return json.dumps({"success": False, "error": "amount must be greater than 0"})

        if not deduction_date or not validate_date(deduction_date):
            return json.dumps({"success": False, "error": "deduction_date must be YYYY-MM-DD"})

        status_value = status.strip().lower() if isinstance(status, str) and status.strip() else "valid"
        if status_value not in {"valid", "invalid_limit_exceeded"}:
            return json.dumps({"success": False, "error": "status must be valid or invalid_limit_exceeded"})

        for deduction_id, deduction in deductions.items():
            if not isinstance(deduction, dict):
                continue
            if (
                str(deduction.get("employee_id")) == employee_id
                and str(deduction.get("deduction_rule_id")) == deduction_rule_id
                and str(deduction.get("cycle_id")) == cycle_id
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Deduction with rule '{deduction_rule_id}' already exists for employee '{employee_id}' "
                            f"in cycle '{cycle_id}' (deduction_id: {deduction_id})"
                        ),
                    }
                )

        deduction_id = generate_id(deductions)
        timestamp = "2025-11-16T23:59:00"

        record = {
            "deduction_id": deduction_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "deduction_rule_id": deduction_rule_id,
            "amount": f"{amount_decimal:.2f}",
            "deduction_date": deduction_date,
            "status": status_value,
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        deductions[deduction_id] = record

        return json.dumps(
            {
                "success": True,
                "message": f"Deduction assigned to employee {employee_id}",
                "deduction": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_deduction_to_employee",
                "description": "Assign a payroll deduction to an employee using a deduction rule and payroll cycle.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {"type": "string", "description": "Employee identifier receiving the deduction."},
                        "deduction_rule_id": {"type": "string", "description": "Deduction rule identifier to apply."},
                        "cycle_id": {"type": "string", "description": "Payroll cycle identifier for the deduction."},
                        "amount": {"type": "number", "description": "Deduction amount; must be greater than 0."},
                        "deduction_date": {"type": "string", "description": "Date of deduction (YYYY-MM-DD)."},
                        "status": {
                            "type": "string",
                            "description": "Optional status override; allowed values: valid, invalid_limit_exceeded.",
                        },
                    },
                    "required": ["employee_id", "deduction_rule_id", "cycle_id", "amount", "deduction_date"],
                },
            },
        }
