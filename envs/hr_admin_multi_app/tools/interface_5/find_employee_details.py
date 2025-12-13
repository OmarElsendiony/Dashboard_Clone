import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class FindEmployeeDetails(Tool):
    """Find employees by id, email, manager, department, or status."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: Optional[str] = None,
        emp_id: Optional[str] = None,
        reporting_manager_id: Optional[str] = None,
        department_id: Optional[str] = None,
        full_name: Optional[str] = None,
        role: Optional[str] = None,
        emp_status: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        employees = data.get("employees", {})
        if not isinstance(employees, dict):
            return json.dumps({"success": False, "error": "Corrupted employees store"})

        # Require at least one filter to avoid returning the entire dataset
        if not any([email, emp_id, reporting_manager_id, department_id, emp_status, full_name, role]):
            return json.dumps({"success": False, "employees": []})

        allowed_statuses = {"active", "inactive", "on_leave", "probation"}
        if emp_status and emp_status.lower() not in allowed_statuses:
            return json.dumps({"success": False, "error": "emp_status must be one of active, inactive, on_leave, probation"})

        def normalize(value: Optional[str]) -> Optional[str]:
            return value.strip().lower() if isinstance(value, str) and value.strip() else None

        def format_employee(record_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
            payload = dict(record)
            payload["employee_id"] = record_id
            return payload

        email_key = normalize(email)
        name_key = normalize(full_name)
        manager_key = normalize(reporting_manager_id)
        dept_key = normalize(department_id)
        status_key = normalize(emp_status)
        role_key = normalize(role)

        if emp_id:
            record = employees.get(emp_id)
            if not record:
                return json.dumps({"success": False, "error": f"Employee '{emp_id}' not found"})
            if email_key and normalize(record.get("email")) != email_key:
                return json.dumps({"success": False, "error": "Employee found but email mismatch"})
            if manager_key and normalize(record.get("manager_id")) != manager_key:
                return json.dumps({"success": False, "error": "Employee found but manager mismatch"})
            if dept_key and normalize(record.get("department_id")) != dept_key:
                return json.dumps({"success": False, "error": "Employee found but department mismatch"})
            if name_key and normalize(record.get("full_name")) != name_key:
                return json.dumps({"success": False, "error": "Employee found but name mismatch"})
            if role_key not in {"admin", "non_admin"}:
                return json.dumps({"success": False, "error": "role must be admin or non_admin"})
            if role_key and normalize(record.get("role")) != role_key:
                return json.dumps({"success": False, "error": "Employee found but role mismatch"})
            if status_key and normalize(record.get("status")) != status_key:
                return json.dumps({"success": False, "error": "Employee found but status mismatch"})
            return json.dumps({"success": True, "employees": [format_employee(emp_id, record)]})

        results = []
        for record_id, record in employees.items():
            if email_key and normalize(record.get("email")) != email_key:
                continue
            if name_key and normalize(record.get("full_name")) != name_key:
                continue
            if manager_key and normalize(record.get("manager_id")) != manager_key:
                continue
            if dept_key and normalize(record.get("department_id")) != dept_key:
                continue
            if role_key and normalize(record.get("role")) != role_key:
                continue
            if status_key and normalize(record.get("status")) != status_key:
                continue
            results.append(format_employee(record_id, record))

        if not results:
            return json.dumps({"success": False, "error": "No employees found matching the criteria"})

        return json.dumps({"success": True, "count": len(results), "employees": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_employee_details",
                "description": (
                    "Return employees filtered by id, email, manager, department, full name, role, or status. "
                    "At least one filter must be supplied."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "emp_id": {
                            "type": "string",
                            "description": "Unique employee identifier to fetch an exact employee.",
                        },
                        "email": {
                            "type": "string",
                            "description": "Corporate email address used to locate an employee.",
                        },
                        "reporting_manager_id": {
                            "type": "string",
                            "description": "Manager identifier; returns direct reports for that manager.",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "Department identifier to list all members in that department.",
                        },
                        "full_name": {
                            "type": "string",
                            "description": "Case-insensitive full-name filter to match a specific employee.",
                        },
                        "role": {
                            "type": "string",
                            "description": "Employee role classification; allowed values are admin or non_admin.",
                        },
                        "emp_status": {
                            "type": "string",
                            "description": "Employment status filter; allowed values: active, inactive, on_leave, probation.",
                        },
                    },
                    "required": [],
                },
            },
        }
