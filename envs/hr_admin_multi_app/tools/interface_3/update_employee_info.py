import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class UpdateEmployeeInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        department_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Update an existing employee record with the provided fields.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee to update (required).
            department_id: The ID of the new department (optional).
            manager_id: The ID of the new manager (optional).
            updates: JSON object containing additional fields to update (optional).
                Supported fields: full_name, email, start_date, base_salary, status, 
                tenure_months, performance_rating, location, role, and various flags.
                status allowed values: 'active', 'inactive', 'on_leave', 'probation'.
                role allowed values: 'admin', 'non_admin'.
        
        Returns:
            JSON string with the updated employee record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})

        employee_id = str(employee_id)
        employees = data.get("employees", {})
        departments = data.get("departments", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        employee = employees[employee_id]

        # Validate that at least one update parameter is provided
        if department_id is None and manager_id is None and not updates:
            return json.dumps({
                "error": "No updates provided. At least one of department_id, manager_id, or updates must be specified."
            })

        # Handle department_id update
        if department_id is not None:
            department_id = str(department_id)
            if department_id not in departments:
                return json.dumps({"error": f"Department with ID '{department_id}' not found"})
            employee["department_id"] = department_id

        # Handle manager_id update
        if manager_id is not None:
            if manager_id:
                manager_id = str(manager_id)
                if manager_id not in employees:
                    return json.dumps({"error": f"Manager with ID '{manager_id}' not found"})
                if manager_id == employee_id:
                    return json.dumps({"error": "Employee cannot be their own manager"})
            employee["manager_id"] = manager_id if manager_id else None

        # Handle additional updates
        if updates and isinstance(updates, dict):
            # Validate status if being updated
            if "status" in updates:
                allowed_statuses = ["active", "inactive", "on_leave", "probation"]
                if updates["status"] not in allowed_statuses:
                    return json.dumps({
                        "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
                    })

            # Validate role if being updated
            if "role" in updates:
                allowed_roles = ["admin", "non_admin"]
                if updates["role"] not in allowed_roles:
                    return json.dumps({
                        "error": f"Invalid role. Allowed values: {', '.join(allowed_roles)}"
                    })

            # Validate email uniqueness if being updated
            if "email" in updates:
                for emp_id, emp in employees.items():
                    if emp_id != employee_id and emp.get("email") == updates["email"]:
                        return json.dumps({"error": f"Employee with email '{updates['email']}' already exists"})

            # Allowed fields to update
            allowed_fields = [
                "full_name", "email", "start_date", "base_salary", "status", 
                "tenure_months", "performance_rating", "location", "role",
                "flag_financial_counseling_recommended", "flag_potential_overtime_violation",
                "flag_requires_payroll_review", "flag_high_offboard_risk",
                "flag_pending_settlement", "flag_requires_finance_approval"
            ]

            for key, value in updates.items():
                if key in allowed_fields:
                    employee[key] = value

        employee["last_updated"] = "2025-11-16T23:59:00"

        return json.dumps(employee)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_employee_info",
                "description": (
                    "Updates an existing employee record with the provided fields. "
                    "Can update department, manager, and other employee attributes. "
                    "Validates that referenced departments and managers exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee to update (required).",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "The ID of the new department (optional).",
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "The ID of the new manager (optional).",
                        },
                        "updates": {
                            "type": "object",
                            "description": (
                                "JSON object containing additional fields to update (optional). "
                                "Supported fields: full_name, email, start_date, base_salary, status, "
                                "tenure_months, performance_rating, location, role, and various flags."
                            ),
                            "properties": {
                                "full_name": {
                                    "type": "string",
                                    "description": "The full name of the employee.",
                                },
                                "email": {
                                    "type": "string",
                                    "description": "The unique email address of the employee.",
                                },
                                "start_date": {
                                    "type": "string",
                                    "description": "The start date in format (YYYY-MM-DD).",
                                },
                                "base_salary": {
                                    "type": "number",
                                    "description": "The base salary of the employee.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The employment status. Allowed values: 'active', 'inactive', 'on_leave', 'probation'.",
                                },
                                "role": {
                                    "type": "string",
                                    "description": "The employee role. Allowed values: 'admin', 'non_admin'.",
                                },
                                "performance_rating": {
                                    "type": "integer",
                                    "description": "Performance rating from 1 to 5.",
                                },
                            },
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }
