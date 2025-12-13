import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class NewEmployee(Tool):
    """Create a new employee record with validated department, manager, and compensation details."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: str,
        emp_name: str,
        emp_dept: str,
        emp_status: str,
        base_pay: float,
        start_date: str,
        role: str = "non_admin",
        emp_manager_id: Optional[str] = None,
    ) -> str:

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        def normalize(value: Optional[str]) -> Optional[str]:
            return value.strip().lower() if isinstance(value, str) and value.strip() else None

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

        employees = data.get("employees")
        departments = data.get("departments")
        if not isinstance(employees, dict) or not isinstance(departments, dict):
            return json.dumps({"success": False, "error": "Missing employees or departments store"})

        if not email or not emp_name or not emp_dept or not emp_status or not start_date:
            return json.dumps({"success": False, "error": "All required fields must be provided"})

        allowed_statuses = {"active", "inactive", "on_leave", "probation"}
        status_normalized = emp_status.strip().lower()
        if status_normalized not in allowed_statuses:
            return json.dumps(
                {"success": False, "error": "emp_status must be one of active, inactive, on_leave, probation"}
            )

        try:
            salary_decimal = Decimal(str(base_pay)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            return json.dumps({"success": False, "error": "base_pay must be a valid number"})

        if salary_decimal <= 0:
            return json.dumps({"success": False, "error": "base_pay must be greater than 0"})

        emp_dept = str(emp_dept)
        department = departments.get(emp_dept)
        if not department:
            return json.dumps({"success": False, "error": f"Department '{emp_dept}' does not exist"})
        if normalize(department.get("status")) != "active":
            return json.dumps({"success": False, "error": f"Department '{emp_dept}' is not active"})

        manager_record = None
        if emp_manager_id:
            emp_manager_id = str(emp_manager_id)
            manager_record = employees.get(emp_manager_id)
            if not manager_record:
                return json.dumps({"success": False, "error": f"Manager '{emp_manager_id}' not found"})
            if normalize(manager_record.get("status")) != "active":
                return json.dumps({"success": False, "error": f"Manager '{emp_manager_id}' is not active"})

        email_key = normalize(email)
        for existing in employees.values():
            if normalize(existing.get("email")) == email_key:
                return json.dumps({"success": False, "error": f"Employee with email '{email}' already exists"})

        if not validate_date(start_date):
            return json.dumps({"success": False, "error": "start_date must be YYYY-MM-DD"})

        role_value = role.strip().lower().replace("-", "_") if isinstance(role, str) else "non_admin"
        if role_value not in {"admin", "non_admin"}:
            return json.dumps({"success": False, "error": "role must be admin or non_admin"})

        location_value = None
        timestamp = "2025-11-16T23:59:00"

        new_employee_id = generate_id(employees)
        new_employee = {
            "employee_id": new_employee_id,
            "manager_id": emp_manager_id,
            "department_id": emp_dept,
            "start_date": start_date,
            "full_name": emp_name,
            "email": email,
            "status": status_normalized,
            "tenure_months": 0,
            "performance_rating": None,
            "base_salary": f"{salary_decimal:.2f}",
            "location": location_value,
            "role": role_value,
            "flag_financial_counseling_recommended": False,
            "flag_potential_overtime_violation": False,
            "flag_requires_payroll_review": False,
            "flag_high_offboard_risk": False,
            "flag_pending_settlement": False,
            "flag_requires_finance_approval": False,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        employees[new_employee_id] = new_employee

        return json.dumps(
            {
                "success": True,
                "message": f"Employee {new_employee_id} created successfully",
                "employee": new_employee,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "new_employee",
                "description": (
                    "Create a new employee profile after validating department status, manager activity, "
                    "employment status enum, compensation, and start date."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Unique corporate email that will be associated with the new employee.",
                        },
                        "emp_name": {
                            "type": "string",
                            "description": "Full name of the employee being created.",
                        },
                        "emp_dept": {
                            "type": "string",
                            "description": "Department identifier where the employee will reside; must reference an active department.",
                        },
                        "emp_status": {
                            "type": "string",
                            "description": "Employment status one of active, inactive, on_leave, probation.",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date for the employee in YYYY-MM-DD format.",
                        },
                        "role": {
                            "type": "string",
                            "description": (
                                "Employee role classification; allowed values are admin or non_admin. Defaults to non_admin."
                            ),
                        },
                        "base_pay": {
                            "type": "number",
                            "description": "Annualized base pay for the employee in USD.",
                        },
                        "emp_manager_id": {
                            "type": "string",
                            "description": "Optional manager employee_id; must reference an active employee when provided.",
                        },
                    },
                    "required": ["email", "emp_name", "emp_dept", "emp_status", "base_pay", "start_date"],
                },
            },
        }
