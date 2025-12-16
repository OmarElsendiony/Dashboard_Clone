import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateEmployee(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        manager_id: Optional[str] = None,
        department_id: str = None,
        start_date: str = None,
        full_name: str = None,
        email: str = None,
        status: Optional[str] = "active",
        tenure_months: Optional[int] = None,
        performance_rating: Optional[int] = None,
        base_salary: float = None,
        flag_financial_counseling_recommended: Optional[bool] = False,
        flag_potential_overtime_violation: Optional[bool] = False,
        flag_requires_payroll_review: Optional[bool] = False,
        flag_high_offboard_risk: Optional[bool] = False,
        flag_pending_settlement: Optional[bool] = False,
        flag_requires_finance_approval: Optional[bool] = False,
    ) -> str:
        """
        Creates a new employee record in the system.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        timestamp = "2025-11-16T23:59:00"
        employees = data.get("employees", {})
        departments = data.get("departments", {})

        # Validate required fields
        if not all(
            [department_id, start_date, full_name, email, base_salary is not None]
        ):
            return json.dumps(
                {
                    "error": "Missing required parameters. Required: department_id, start_date, full_name, email, base_salary"
                }
            )

        # Validate department exists
        if department_id not in departments:
            return json.dumps(
                {"error": f"Department with ID '{department_id}' not found"}
            )

        # Validate manager exists if provided
        if manager_id and manager_id not in employees:
            return json.dumps({"error": f"Manager with ID '{manager_id}' not found"})

        # Validate email uniqueness
        for existing_employee in employees.values():
            if existing_employee.get("email") == email:
                return json.dumps(
                    {"error": f"Employee with email '{email}' already exists"}
                )

        # Validate status
        valid_statuses = ["active", "inactive", "probation"]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                }
            )

        # Validate performance rating if provided
        if performance_rating is not None and (
            performance_rating < 1 or performance_rating > 5
        ):
            return json.dumps({"error": "Performance rating must be between 1 and 5"})

        # Validate base salary
        if base_salary <= 0:
            return json.dumps({"error": "Base salary must be greater than 0"})

        # Validate tenure_months if provided
        if tenure_months is not None and tenure_months < 0:
            return json.dumps({"error": "tenure_months must be non-negative"})

        # Generate new employee ID
        new_employee_id = generate_id(employees)

        # Create new employee record
        new_employee = {
            "employee_id": new_employee_id,
            "manager_id": manager_id,
            "department_id": department_id,
            "start_date": start_date,
            "full_name": full_name,
            "email": email,
            "status": status,
            "tenure_months": tenure_months,
            "performance_rating": performance_rating,
            "base_salary": base_salary,
            "flag_financial_counseling_recommended": flag_financial_counseling_recommended,
            "flag_potential_overtime_violation": flag_potential_overtime_violation,
            "flag_requires_payroll_review": flag_requires_payroll_review,
            "flag_high_offboard_risk": flag_high_offboard_risk,
            "flag_pending_settlement": flag_pending_settlement,
            "flag_requires_finance_approval": flag_requires_finance_approval,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        employees[new_employee_id] = new_employee

        return json.dumps(
            {
                "success": True,
                "message": f"Employee {new_employee_id} created successfully",
                "employee_data": new_employee,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_employee",
                "description": "Creates a new employee record in the HR system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "manager_id": {
                            "type": "string",
                            "description": "ID of the employee's manager (optional, must exist in employees table)",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "ID of the department (required, must exist in departments table)",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Employee start date in YYYY-MM-DD format (required)",
                        },
                        "full_name": {
                            "type": "string",
                            "description": "Full name of the employee (required)",
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address of the employee (required, must be unique)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Employment status: 'active', 'inactive', 'probation' (optional, defaults to 'active')",
                        },
                        "tenure_months": {
                            "type": "integer",
                            "description": "Number of months employed (optional)",
                        },
                        "performance_rating": {
                            "type": "integer",
                            "description": "Performance rating from 1 to 5 (optional)",
                        },
                        "base_salary": {
                            "type": "number",
                            "description": "Base salary amount (required, must be greater than 0)",
                        },
                        "flag_financial_counseling_recommended": {
                            "type": "boolean",
                            "description": "Flag indicating if financial counseling is recommended: True/False (optional, defaults to False)",
                        },
                        "flag_potential_overtime_violation": {
                            "type": "boolean",
                            "description": "Flag indicating potential overtime violation: True/False (optional, defaults to False)",
                        },
                        "flag_requires_payroll_review": {
                            "type": "boolean",
                            "description": "Flag indicating if payroll review is required: True/False (optional, defaults to False)",
                        },
                        "flag_high_offboard_risk": {
                            "type": "boolean",
                            "description": "Flag indicating high offboarding risk: True/False (optional, defaults to False)",
                        },
                        "flag_pending_settlement": {
                            "type": "boolean",
                            "description": "Flag indicating pending settlement: True/False (optional, defaults to False)",
                        },
                        "flag_requires_finance_approval": {
                            "type": "boolean",
                            "description": "Flag indicating if finance approval is required: True/False (optional, defaults to False)",
                        },
                    },
                    "required": [],
                },
            },
        }
