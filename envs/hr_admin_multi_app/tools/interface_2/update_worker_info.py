import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateWorkerInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        department_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        status: Optional[str] = None,
        base_salary: Optional[float] = None,
        location: Optional[str] = None,
        role: Optional[str] = None,
        tenure_months: Optional[str] = None,
    ) -> str:
        """
        Update worker information in the HR system.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        employees = data.get("employees", {})

        if str(employee_id) not in employees:
            return json.dumps(
                {"success": False, "error": f"Employee {employee_id} not found"}
            )

        employee = employees[str(employee_id)]

        # Track what was updated
        updated_fields = []

        # Update fields if provided
        if full_name is not None:
            employee["full_name"] = full_name
            updated_fields.append("full_name")

        if email is not None:
            # Check if email is already used by another employee
            for emp_id, emp in employees.items():
                if emp_id != str(employee_id) and emp.get("email") == email:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Email '{email}' is already in use by another employee",
                        }
                    )
            employee["email"] = email
            updated_fields.append("email")

        if department_id is not None:
            # Verify department exists
            departments = data.get("departments", {})
            if str(department_id) not in departments:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Department {department_id} not found",
                    }
                )
            employee["department_id"] = str(department_id)
            updated_fields.append("department_id")

        if manager_id is not None:
            # Verify manager exists
            if str(manager_id) not in employees:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Manager {manager_id} not found",
                    }
                )
            employee["manager_id"] = str(manager_id)
            updated_fields.append("manager_id")

        if status is not None:
            # Validate status
            valid_statuses = ["active", "inactive", "probation", "on_leave"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    }
                )
            employee["status"] = status
            updated_fields.append("status")

        if base_salary is not None:
            employee["base_salary"] = str(base_salary)
            updated_fields.append("base_salary")

        if location is not None:
            employee["location"] = location
            updated_fields.append("location")

        if role is not None:
            # Validate role
            valid_roles = ["admin", "non_admin"]
            if role not in valid_roles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid role. Must be one of: {', '.join(valid_roles)}",
                    }
                )
            employee["role"] = role
            updated_fields.append("role")

        if tenure_months is not None:
            employee["tenure_months"] = int(tenure_months)
            updated_fields.append("tenure_months")

        # Update last_updated timestamp
        employee["last_updated"] = "2025-12-12T12:00:00"

        if not updated_fields:
            return json.dumps(
                {
                    "success": False,
                    "error": "No fields to update. Please provide at least one field to update.",
                }
            )

        return json.dumps(
            {
                "success": True,
                "message": f"Employee {employee_id} updated successfully",
                "updated_fields": updated_fields,
                "employee_data": employee,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_worker_info",
                "description": "Updates worker information in the HR system. You can update one or more fields including full name, email, department, manager, status, base salary, location, role, and tenure months. The employee must exist in the system. Email addresses must be unique across all employees.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The unique identifier of the employee to update. Required field.",
                        },
                        "full_name": {
                            "type": "string",
                            "description": "The full name of the employee. Optional field.",
                        },
                        "email": {
                            "type": "string",
                            "description": "The email address of the employee. Must be unique across all employees. Optional field.",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "The department ID the employee belongs to. The department must exist in the system. Optional field.",
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "The employee ID of the manager. The manager must exist in the system. Optional field.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The employment status. Valid values are: 'active', 'inactive', 'probation', 'on_leave'. Optional field.",
                        },
                        "base_salary": {
                            "type": "number",
                            "description": "The base salary amount. Optional field.",
                        },
                        "location": {
                            "type": "string",
                            "description": "The work location of the employee. Optional field.",
                        },
                        "role": {
                            "type": "string",
                            "description": "The role type. Valid values are: 'admin', 'non_admin'. Optional field.",
                        },
                        "tenure_months": {
                            "type": "string",
                            "description": "The number of months the employee has been with the company. Optional field.",
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }

