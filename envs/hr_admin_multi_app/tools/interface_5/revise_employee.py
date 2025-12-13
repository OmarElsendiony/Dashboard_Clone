import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class ReviseEmployee(Tool):
    """
    Update an existing employee record.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        fields: Dict[str, Any],
    ) -> str:
        """
        Apply updates supplied in the fields object to a targeted employee.

        Expected field keys:
        - employee_id (required): identifies the record to update.
        - email, emp_name, emp_dept, emp_status, base_pay, emp_manager_id (optional updates).
        - onboarding_data (optional JSON string) supporting updates to start_date, role.
        """

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

        if not isinstance(fields, dict):
            return json.dumps({"success": False, "error": "fields payload must be an object"})

        employees = data.get("employees")
        departments = data.get("departments")

        if not isinstance(employees, dict) or not isinstance(departments, dict):
            return json.dumps({"success": False, "error": "Missing employees or departments store"})

        employee_id = fields.get("employee_id")
        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})

        employee = employees.get(employee_id)
        if not employee:
            return json.dumps({"success": False, "error": f"Employee '{employee_id}' not found"})

        updates_applied = False
        allowed_statuses = {"active", "inactive", "on_leave", "probation"}
        timestamp = "2025-12-12T12:00:00"

        # Email update
        if "email" in fields:
            new_email = fields.get("email")
            if not isinstance(new_email, str) or not new_email.strip():
                return json.dumps({"success": False, "error": "email must be a non-empty string"})
            normalized_email = normalize(new_email)
            for other_id, record in employees.items():
                if other_id == employee_id:
                    continue
                if normalize(record.get("email")) == normalized_email:
                    return json.dumps({"success": False, "error": f"Employee with email '{new_email}' already exists"})
            employee["email"] = new_email
            updates_applied = True

        # Name update
        if "emp_name" in fields:
            new_name = fields.get("emp_name")
            if not isinstance(new_name, str) or not new_name.strip():
                return json.dumps({"success": False, "error": "emp_name must be a non-empty string"})
            employee["full_name"] = new_name
            updates_applied = True

        # Department update
        if "emp_dept" in fields:
            new_dept = fields.get("emp_dept")
            if not isinstance(new_dept, str) or not new_dept.strip():
                return json.dumps({"success": False, "error": "emp_dept must be a non-empty string"})
            department = departments.get(new_dept)
            if not department:
                return json.dumps({"success": False, "error": f"Department '{new_dept}' does not exist"})
            if normalize(department.get("status")) != "active":
                return json.dumps({"success": False, "error": f"Department '{new_dept}' is not active"})
            employee["department_id"] = new_dept
            updates_applied = True

        # Status update
        if "emp_status" in fields:
            new_status = fields.get("emp_status")
            if not isinstance(new_status, str):
                return json.dumps({"success": False, "error": "emp_status must be a string"})
            normalized_status = new_status.strip().lower()
            if normalized_status not in allowed_statuses:
                return json.dumps(
                    {"success": False, "error": "emp_status must be one of active, inactive, on_leave, probation"}
                )
            employee["status"] = normalized_status
            updates_applied = True

        # Base pay update
        if "base_pay" in fields:
            try:
                salary_decimal = Decimal(str(fields.get("base_pay"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except (InvalidOperation, ValueError):
                return json.dumps({"success": False, "error": "base_pay must be a valid number"})
            if salary_decimal <= 0:
                return json.dumps({"success": False, "error": "base_pay must be greater than 0"})
            employee["base_salary"] = f"{salary_decimal:.2f}"
            updates_applied = True

        # Manager update
        if "emp_manager_id" in fields:
            manager_id = fields.get("emp_manager_id")
            if manager_id:
                if manager_id == employee_id:
                    return json.dumps({"success": False, "error": "Employee cannot be their own manager"})
                manager_record = employees.get(manager_id)
                if not manager_record:
                    return json.dumps({"success": False, "error": f"Manager '{manager_id}' not found"})
                if normalize(manager_record.get("status")) != "active":
                    return json.dumps({"success": False, "error": f"Manager '{manager_id}' is not active"})
                employee["manager_id"] = manager_id
            else:
                employee["manager_id"] = None
            updates_applied = True

        # Onboarding data updates
        onboarding_payload_raw = fields.get("onboarding_data")
        if onboarding_payload_raw:
            try:
                onboarding_payload = json.loads(onboarding_payload_raw)
            except json.JSONDecodeError:
                return json.dumps({"success": False, "error": "onboarding_data must be valid JSON"})
            if not isinstance(onboarding_payload, dict):
                return json.dumps({"success": False, "error": "onboarding_data must encode an object"})

            if "start_date" in onboarding_payload:
                start_date = onboarding_payload.get("start_date")
                if not start_date or not validate_date(start_date):
                    return json.dumps({"success": False, "error": "onboarding_data.start_date must be YYYY-MM-DD"})
                employee["start_date"] = start_date
                updates_applied = True

            if "role" in onboarding_payload:
                role_value = onboarding_payload.get("role")
                if isinstance(role_value, str):
                    role_value = role_value.strip().lower().replace("-", "_")
                else:
                    return json.dumps({"success": False, "error": "onboarding_data.role must be a string"})
                if role_value not in {"admin", "non_admin"}:
                    return json.dumps({"success": False, "error": "onboarding_data.role must be admin or non_admin"})
                employee["role"] = role_value
                updates_applied = True

            if "location" in onboarding_payload:
                location_value = onboarding_payload.get("location")
                if location_value is None:
                    employee["location"] = None
                elif isinstance(location_value, str):
                    employee["location"] = location_value.strip() or None
                else:
                    return json.dumps({"success": False, "error": "onboarding_data.location must be a string or null"})
                updates_applied = True

        if not updates_applied:
            return json.dumps({"success": False, "error": "No valid fields supplied for update"})

        employee["last_updated"] = timestamp

        return json.dumps(
            {
                "success": True,
                "message": f"Employee {employee_id} updated successfully",
                "employee": employee,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "revise_employee",
                "description": (
                    "Update an employee record by supplying a fields object that may include email, department, "
                    "status, compensation, manager, and onboarding metadata."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fields": {
                            "type": "object",
                            "description": (
                                "Payload describing which attributes to update. Must include employee_id and can include "
                                "email, emp_name, emp_dept, emp_status, base_pay, emp_manager_id, and onboarding_data "
                                "(JSON for start_date/role/location)."
                            ),
                            "properties": {
                                "employee_id": {
                                    "type": "string",
                                    "description": "Identifier of the employee record that will be updated.",
                                },
                                "email": {
                                    "type": "string",
                                    "description": "New email address; must be unique among employees.",
                                },
                                "emp_name": {
                                    "type": "string",
                                    "description": "Full name replacement for the employee.",
                                },
                                "emp_dept": {
                                    "type": "string",
                                    "description": "Department identifier; department must exist and be active.",
                                },
                                "emp_status": {
                                    "type": "string",
                                    "description": "Employment status; allowed values: active, inactive, on_leave, probation.",
                                },
                                "base_pay": {
                                    "type": "number",
                                    "description": "New base salary amount in USD.",
                                },
                                "emp_manager_id": {
                                    "type": "string",
                                    "description": "Manager employee_id; must reference a different active employee.",
                                },
                                "onboarding_data": {
                                    "type": "string",
                                    "description": (
                                        "JSON string that can update onboarding fields such as start_date (YYYY-MM-DD), "
                                        "role (admin/non_admin), and location."
                                    ),
                                },
                            },
                            "required": ["employee_id"],
                        }
                    },
                    "required": ["fields"],
                },
            },
        }
