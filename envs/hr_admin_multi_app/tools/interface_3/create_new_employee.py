import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateNewEmployee(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        full_name: str,
        email: str,
        department_id: str,
        start_date: str,
        base_salary: float,
        document_url: str,
        manager_id: Optional[str] = None,
        status: str = "active",
    ) -> str:
        """
        Create a new employee record in the system along with an associated contract.
        
        Args:
            data: The database dictionary containing all tables.
            full_name: The full name of the employee (required).
            email: The unique email address of the employee (required).
            department_id: The ID of the department the employee belongs to (required).
            start_date: The start date of the employee in format (YYYY-MM-DD) (required).
            base_salary: The base salary of the employee (required).
            document_url: The URL link to the employee's digital contract document (required).
            manager_id: The ID of the employee's manager (optional).
            status: The employment status. Allowed values: 'active', 'inactive', 'on_leave', 'probation'. 
                Defaults to 'active'.
        
        Returns:
            JSON string with the created employee and contract records.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            max_id = 0
            for k in table.keys():
                try:
                    max_id = max(max_id, int(k))
                except ValueError:
                    continue
            return str(max_id + 1)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not full_name:
            return json.dumps({"error": "Missing required parameter: full_name is required"})
        if not email:
            return json.dumps({"error": "Missing required parameter: email is required"})
        if not department_id:
            return json.dumps({"error": "Missing required parameter: department_id is required"})
        if not start_date:
            return json.dumps({"error": "Missing required parameter: start_date is required"})
        if base_salary is None:
            return json.dumps({"error": "Missing required parameter: base_salary is required"})
        if not document_url:
            return json.dumps({"error": "Missing required parameter: document_url is required"})

        # Validate status
        allowed_statuses = ["active", "inactive", "on_leave", "probation"]
        if status not in allowed_statuses:
            return json.dumps({
                "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
            })

        # Access employees and departments tables
        employees = data.get("employees", {})
        departments = data.get("departments", {})

        # Validate department exists
        department_id = str(department_id)
        if department_id not in departments:
            return json.dumps({"error": f"Department with ID '{department_id}' not found"})

        # Validate manager exists if provided
        if manager_id:
            manager_id = str(manager_id)
            if manager_id not in employees:
                return json.dumps({"error": f"Manager with ID '{manager_id}' not found"})

        # Check for duplicate email
        for emp_id, emp in employees.items():
            if emp.get("email") == email:
                return json.dumps({"error": f"Employee with email '{email}' already exists"})

        # Generate new employee ID
        employee_id = generate_id(employees)

        # Create employee record
        timestamp = "2025-12-12T12:00:00"
        new_employee = {
            "employee_id": employee_id,
            "full_name": full_name,
            "email": email,
            "department_id": department_id,
            "manager_id": manager_id,
            "start_date": start_date,
            "base_salary": float(base_salary),
            "status": status,
            "tenure_months": 0,
            "performance_rating": None,
            "location": None,
            "role": "non_admin",
            "flag_financial_counseling_recommended": False,
            "flag_potential_overtime_violation": False,
            "flag_requires_payroll_review": False,
            "flag_high_offboard_risk": False,
            "flag_pending_settlement": False,
            "flag_requires_finance_approval": False,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        employees[employee_id] = new_employee
        data["employees"] = employees

        # Create contract for the new employee
        contracts = data.get("contracts", {})
        contract_id = generate_id(contracts)
        new_contract = {
            "contract_id": contract_id,
            "employee_id": employee_id,
            "document_url": document_url,
            "created_at": timestamp,
            "is_terminated": False,
            "termination_date": None,
            "last_updated": timestamp,
        }
        contracts[contract_id] = new_contract
        data["contracts"] = contracts

        return json.dumps({
            "employee": new_employee,
            "contract": new_contract,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_employee",
                "description": (
                    "Creates a new employee record in the system along with an associated contract. "
                    "Requires basic employee information including name, email, department, start date, and salary. "
                    "Optionally assigns a manager to the new employee. "
                    "Returns both the employee and contract records."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "full_name": {
                            "type": "string",
                            "description": "The full name of the employee (required).",
                        },
                        "email": {
                            "type": "string",
                            "description": "The unique email address of the employee (required).",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "The ID of the department the employee belongs to (required).",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "The start date of the employee in format (YYYY-MM-DD) (required).",
                        },
                        "base_salary": {
                            "type": "number",
                            "description": "The base salary of the employee (required).",
                        },
                        "document_url": {
                            "type": "string",
                            "description": "The URL link to the employee's digital contract document (required).",
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "The ID of the employee's manager (optional).",
                        },
                        "status": {
                            "type": "string",
                            "description": "The employment status. Allowed values: 'active', 'inactive', 'on_leave', 'probation'. Defaults to 'active'.",
                        },
                    },
                    "required": ["full_name", "email", "department_id", "start_date", "base_salary", "document_url"],
                },
            },
        }
