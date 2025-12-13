import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class TerminateEmployeeRecord(Tool):
    """
    Record an employee termination by updating their status and creating an exit case entry.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        exit_data: Dict[str, Any],
        email: Optional[str] = None,
        employee_id: Optional[str] = None,
    ) -> str:
        """
        Capture the exit reason for employee offboarding.
        """

        def normalize(value: Optional[str]) -> Optional[str]:
            return value.strip().lower() if isinstance(value, str) and value.strip() else None

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        def validate_date(date_str: str) -> bool:
            if not isinstance(date_str, str):
                return False
            parts = date_str.split("-")
            if len(parts) != 3:
                return False
            try:
                year, month, day = map(int, parts)
            except ValueError:
                return False
            return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        if not isinstance(exit_data, dict):
            return json.dumps({"success": False, "error": "exit_data must be an object"})

        employees = data.get("employees")
        exit_cases = data.get("exit_cases")

        if not isinstance(employees, dict) or not isinstance(exit_cases, dict):
            return json.dumps({"success": False, "error": "Missing employees or exit_cases store"})

        if not email and not employee_id:
            return json.dumps({"success": False, "error": "Either employee_id or email must be provided"})

        allowed_reasons = {
            "misconduct",
            "security_breach",
            "policy_violation",
            "voluntary_resignation",
            "layoff",
        }
        reason_value = exit_data.get("reason")
        reason_normalized = normalize(reason_value)
        if not reason_normalized or reason_normalized not in allowed_reasons:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        "reason must be one of misconduct, security_breach, policy_violation, "
                        "voluntary_resignation, layoff"
                    ),
                }
            )

        exit_date = exit_data.get("exit_date")
        if not exit_date or not validate_date(exit_date):
            return json.dumps({"success": False, "error": "exit_data.exit_date must be YYYY-MM-DD"})

        clearance_status = exit_data.get("exit_clearance_status", "pending")
        if clearance_status not in {"pending", "cleared"}:
            return json.dumps({"success": False, "error": "exit_data.exit_clearance_status must be pending or cleared"})

        exit_notes = exit_data.get("notes")

        employee_record = None
        identifier = None

        if employee_id:
            employee_record = employees.get(employee_id)
            identifier = employee_id
            if not employee_record:
                return json.dumps({"success": False, "error": f"Employee '{employee_id}' not found"})
        if email:
            normalized_email = normalize(email)
            # If employee_id already resolved and email also provided, ensure consistency
            if employee_record:
                if normalize(employee_record.get("email")) != normalized_email:
                    return json.dumps({"success": False, "error": "Provided email does not match employee record"})
            else:
                for emp_id, record in employees.items():
                    if normalize(record.get("email")) == normalized_email:
                        employee_record = record
                        identifier = emp_id
                        break
                if not employee_record:
                    return json.dumps({"success": False, "error": f"Employee with email '{email}' not found"})

        if not identifier or not employee_record:
            return json.dumps({"success": False, "error": "Unable to resolve employee"})

        if normalize(employee_record.get("status")) == "inactive":
            return json.dumps({"success": False, "error": "Employee is already inactive"})

        for case in exit_cases.values():
            if case.get("employee_id") == identifier:
                return json.dumps({"success": False, "error": f"Exit case already exists for employee '{identifier}'"})

        timestamp = "2025-12-12T12:00:00"

        # employee_record["status"] = "inactive"
        # employee_record["last_updated"] = timestamp

        exit_case_id = generate_id(exit_cases)
        exit_case = {
            "exit_case_id": exit_case_id,
            "employee_id": identifier,
            "reason": reason_normalized,
            "exit_date": exit_date,
            "exit_clearance_status": clearance_status,
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        if exit_notes:
            exit_case["notes"] = exit_notes
        exit_cases[exit_case_id] = exit_case

        return json.dumps(
            {
                "success": True,
                # "message": f"Employee {identifier} terminated successfully",
                # "employee": employee_record,
                "exit_case": exit_case,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "terminate_employee_record",
                "description": (
                    "This is the first steps towards employee offboarding by creating an exit case. "
                    "Log an exit case for the employee identified by employee_id or email"
                    "with the provided reason."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exit_data": {
                            "type": "object",
                            "description": (
                                "Object describing the exit action. Requires reason and exit_date, and can include "
                                "exit_clearance_status (pending/cleared) and notes."
                            ),
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Employee identifier for the record to terminate.",
                        },
                        "email": {
                            "type": "string",
                            "description": "Employee email.",
                        },
                    },
                    "required": ["exit_data"],
                },
            },
        }
