import json
from datetime import datetime
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateEnrollment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        plan_id: str,
        start_date: str,
        is_active: bool = True,
    ) -> str:
        """Create a benefit enrollment record."""

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        enrollments = data.setdefault("benefit_enrollments", {})
        if not isinstance(enrollments, dict):
            return json.dumps(
                {"success": False, "error": "Invalid benefit_enrollments structure"}
            )

        def require_str(value: Optional[str], field: str) -> str:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
            return value.strip()

        try:
            employee_id = require_str(employee_id, "employee_id")
            plan_id = require_str(plan_id, "plan_id")
            start_date = require_str(start_date, "start_date")
        except ValueError as exc:
            return json.dumps({"success": False, "error": str(exc)})

        if not isinstance(is_active, bool):
            return json.dumps(
                {"success": False, "error": "is_active must be a boolean"}
            )

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            return json.dumps(
                {"success": False, "error": "start_date must use YYYY-MM-DD format"}
            )

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            numeric = [int(k) for k in table.keys() if str(k).isdigit()]
            return str(max(numeric, default=0) + 1)

        enrollment_id = generate_id(enrollments)

        timestamp = "2025-11-16T23:59:00"
        creation_dt = datetime.strptime(timestamp.split("T")[0], "%Y-%m-%d").date()
        if start_dt < creation_dt:
            return json.dumps(
                {
                    "success": False,
                    "error": "start_date cannot be earlier than the creation date",
                }
            )

        record = {
            "enrollment_id": enrollment_id,
            "employee_id": employee_id,
            "plan_id": plan_id,
            "start_date": start_date,
            "is_active": is_active,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        enrollments[enrollment_id] = record

        return json.dumps(
            {
                "success": True,
                "message": "Benefit enrollment created",
                "benefit_enrollment": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_enrollment",
                "description": "Create a benefit enrollment record with given parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Id of Employee to enroll.",
                        },
                        "plan_id": {
                            "type": "string",
                            "description": "Benefit plan id.",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Coverage start date (YYYY-MM-DD).",
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "Flag indicating if the enrollment is active (default True).",
                        },
                    },
                    "required": ["employee_id", "plan_id", "start_date"],
                },
            },
        }
