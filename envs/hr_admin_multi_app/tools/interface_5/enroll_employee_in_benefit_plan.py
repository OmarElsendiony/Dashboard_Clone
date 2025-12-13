import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class EnrollEmployeeInBenefitPlan(Tool):
    """Enroll an employee into a benefit plan with validation against duplicates and active entities."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        plan_id: str,
        start_date: str,
        is_active: Optional[bool] = True,
    ) -> str:
        """
        Create a benefit enrollment entry.

        Requires employee_id, plan_id, and start_date (YYYY-MM-DD). is_active defaults to True.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        def validate_date(date_str: str) -> bool:
            try:
                parts = date_str.split("-")
                if len(parts) != 3:
                    return False
                year, month, day = map(int, parts)
            except ValueError:
                return False
            return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        employees = data.get("employees")
        benefit_plans = data.get("benefit_plans")
        benefit_enrollments = data.get("benefit_enrollments")
        if not isinstance(employees, dict) or not isinstance(benefit_plans, dict) or not isinstance(benefit_enrollments, dict):
            return json.dumps({"success": False, "error": "Missing employees, benefit_plans, or benefit_enrollments store"})

        if not employee_id or employee_id not in employees:
            return json.dumps({"success": False, "error": f"Employee '{employee_id}' not found"})

        plan = benefit_plans.get(plan_id)
        if not plan:
            return json.dumps({"success": False, "error": f"Benefit plan '{plan_id}' not found"})
        if str(plan.get("status", "")).strip().lower() != "active":
            return json.dumps({"success": False, "error": "Benefit plan must be active for enrollment"})
        if str(plan.get("enrollment_window", "")).strip().lower() != "open":
            return json.dumps({"success": False, "error": "Benefit plan enrollment window must be open"})

        if not start_date or not validate_date(start_date):
            return json.dumps({"success": False, "error": "start_date must be YYYY-MM-DD"})

        for enrollment in benefit_enrollments.values():
            if enrollment.get("employee_id") == employee_id and enrollment.get("plan_id") == plan_id:
                return json.dumps({"success": False, "error": "Employee already enrolled in this plan"})

        timestamp = "2025-11-16T23:59:00"
        enrollment_id = generate_id(benefit_enrollments)
        record = {
            "enrollment_id": enrollment_id,
            "employee_id": employee_id,
            "plan_id": plan_id,
            "start_date": start_date,
            "is_active": bool(is_active) if is_active is not None else True,
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        benefit_enrollments[enrollment_id] = record

        return json.dumps(
            {
                "success": True,
                "message": f"Employee {employee_id} enrolled in plan {plan_id}",
                "enrollment": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "enroll_employee_in_benefit_plan",
                "description": "Enroll an employee into a benefit plan after validating plan availability.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {"type": "string", "description": "Employee id."},
                        "plan_id": {"type": "string", "description": "Benefit plan id."},
                        "start_date": {"type": "string", "description": "Enrollment start date (YYYY-MM-DD)."},
                        "is_active": {"type": "boolean", "description": "Whether the enrollment is active."},
                    },
                    "required": ["employee_id", "plan_id", "start_date"],
                },
            },
        }
