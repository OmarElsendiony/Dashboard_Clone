import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateEmployee(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str = None,
        manager_id: Optional[str] = None,
        department_id: Optional[str] = None,
        start_date: Optional[str] = None,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        tenure_months: Optional[int] = None,
        performance_rating: Optional[int] = None,
        base_salary: Optional[float] = None,
        flag_financial_counseling_recommended: Optional[bool] = None,
        flag_potential_overtime_violation: Optional[bool] = None,
        flag_requires_payroll_review: Optional[bool] = None,
        flag_high_offboard_risk: Optional[bool] = None,
        flag_pending_settlement: Optional[bool] = None,
        flag_requires_finance_approval: Optional[bool] = None,
    ) -> str:
        """
        Updates an existing employee record in the system.
        """

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        timestamp = "2025-11-16T23:59:00"
        employees = data.get("employees", {})
        departments = data.get("departments", {})

        # Validate required field
        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id"})

        # Check if employee exists
        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        employee = employees[employee_id]

        # Validate department if provided
        if department_id and department_id not in departments:
            return json.dumps(
                {"error": f"Department with ID '{department_id}' not found"}
            )

        # Validate manager if provided
        if manager_id and manager_id not in employees:
            return json.dumps({"error": f"Manager with ID '{manager_id}' not found"})

        # Validate email uniqueness if provided
        if email:
            for emp_id, existing_employee in employees.items():
                if emp_id != employee_id and existing_employee.get("email") == email:
                    return json.dumps(
                        {"error": f"Employee with email '{email}' already exists"}
                    )

        # Validate status if provided
        if status:
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

        # Validate base salary if provided
        if base_salary is not None and base_salary <= 0:
            return json.dumps({"error": "Base salary must be greater than 0"})

        # Validate tenure_months if being updated
        if tenure_months is not None and tenure_months < 0:
            return json.dumps({"error": "tenure_months must be non-negative"})

        # Update employee fields
        if manager_id is not None:
            employee["manager_id"] = manager_id
        if department_id is not None:
            employee["department_id"] = department_id
        if start_date is not None:
            employee["start_date"] = start_date
        if full_name is not None:
            employee["full_name"] = full_name
        if email is not None:
            employee["email"] = email
        if status is not None:
            employee["status"] = status
        if tenure_months is not None:
            employee["tenure_months"] = tenure_months
        if performance_rating is not None:
            employee["performance_rating"] = performance_rating
        if base_salary is not None:
            employee["base_salary"] = base_salary
        if flag_financial_counseling_recommended is not None:
            employee["flag_financial_counseling_recommended"] = (
                flag_financial_counseling_recommended
            )
        if flag_potential_overtime_violation is not None:
            employee["flag_potential_overtime_violation"] = (
                flag_potential_overtime_violation
            )
        if flag_requires_payroll_review is not None:
            employee["flag_requires_payroll_review"] = flag_requires_payroll_review
        if flag_high_offboard_risk is not None:
            employee["flag_high_offboard_risk"] = flag_high_offboard_risk
        if flag_pending_settlement is not None:
            employee["flag_pending_settlement"] = flag_pending_settlement
        if flag_requires_finance_approval is not None:
            employee["flag_requires_finance_approval"] = flag_requires_finance_approval

        employee["last_updated"] = timestamp

        return json.dumps(
            {
                "success": True,
                "message": f"Employee {employee_id} updated successfully",
                "employee_data": employee,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_employee",
                "description": "Updates an existing employee record in the HR system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee to update (required)",
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "ID of the employee's manager (optional, must exist in employees table)",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "ID of the department (optional, must exist in departments table)",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Employee start date in YYYY-MM-DD format (optional)",
                        },
                        "full_name": {
                            "type": "string",
                            "description": "Full name of the employee (optional)",
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address of the employee (optional, must be unique)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Employment status: 'active', 'inactive', 'probation' (optional)",
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
                            "description": "Base salary amount (optional, must be greater than 0)",
                        },
                        "flag_financial_counseling_recommended": {
                            "type": "boolean",
                            "description": "Flag indicating if financial counseling is recommended: True/False (optional)",
                        },
                        "flag_potential_overtime_violation": {
                            "type": "boolean",
                            "description": "Flag indicating potential overtime violation: True/False (optional)",
                        },
                        "flag_requires_payroll_review": {
                            "type": "boolean",
                            "description": "Flag indicating if payroll review is required: True/False (optional)",
                        },
                        "flag_high_offboard_risk": {
                            "type": "boolean",
                            "description": "Flag indicating high offboarding risk: True/False (optional)",
                        },
                        "flag_pending_settlement": {
                            "type": "boolean",
                            "description": "Flag indicating pending settlement: True/False (optional)",
                        },
                        "flag_requires_finance_approval": {
                            "type": "boolean",
                            "description": "Flag indicating if finance approval is required: True/False (optional)",
                        },
                    },
                    "required": [],
                },
            },
        }
