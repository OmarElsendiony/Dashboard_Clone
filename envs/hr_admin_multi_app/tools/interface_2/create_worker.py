import json
from datetime import datetime, date
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateWorker(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        full_name: str,
        email: str,
        department_id: str,
        manager_id: Optional[str] = None,
        start_date: Optional[str] = None,
        base_salary: float = 0.0,
        location: Optional[str] = None,
        role: str = "worker",
    ) -> str:
        """
        Create a new worker (employee) in the HR system.
        """
        
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        
        employees = data.get("employees", {})
        departments = data.get("departments", {})
        
        # Validate required fields
        if not all([full_name, email, department_id]):
            return json.dumps({
                "success": False,
                "error": "Missing required parameters: full_name, email, department_id"
            })
        
        # Validate department exists
        if department_id not in departments:
            return json.dumps({
                "success": False,
                "error": f"Department with ID '{department_id}' not found"
            })
        
        # Validate manager exists if provided
        if manager_id is not None and manager_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"Manager with ID '{manager_id}' not found"
            })
        
        # Check for duplicate email
        for emp in employees.values():
            if emp.get("email") == email:
                return json.dumps({
                    "success": False,
                    "error": f"Employee with email '{email}' already exists"
                })
        
        # Handle start_date - if None, use today's date (but we use fixed timestamp)
        # Since we can't use date.now(), if start_date is None, we'll use the date from timestamp
        if start_date is None:
            start_date = "2025-12-12"  # Extract date from timestamp
        else:
            # Validate date format (YYYY-MM-DD)
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid date format for start_date. Expected YYYY-MM-DD, got '{start_date}'"
                })
        
        # Calculate tenure_months from start_date to timestamp date
        timestamp_date = date(2025, 12, 12)  # From timestamp "2025-12-12T12:00:00"
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        # Calculate months difference
        years_diff = timestamp_date.year - start_date_obj.year
        months_diff = timestamp_date.month - start_date_obj.month
        tenure_months = years_diff * 12 + months_diff
        if timestamp_date.day < start_date_obj.day:
            tenure_months -= 1
        if tenure_months < 0:
            tenure_months = 0
        
        # Map role to role_enum values (admin or non_admin)
        # If role is 'worker', default to 'non_admin'
        role_enum = "non_admin"
        if role.lower() == "admin":
            role_enum = "admin"
        
        # Generate new employee ID
        employee_id = generate_id(employees)
        timestamp = "2025-12-12T12:00:00"
        
        # Create new employee record
        new_employee = {
            "employee_id": employee_id,
            "manager_id": manager_id,
            "department_id": department_id,
            "start_date": start_date,
            "full_name": full_name,
            "email": email,
            "status": "active",
            "tenure_months": tenure_months,
            "performance_rating": None,  # Not set during creation
            "base_salary": str(base_salary),
            "location": location,
            "role": role_enum,
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
        
        return json.dumps({
            "success": True,
            "employee_id": employee_id,
            "full_name": full_name,
            "email": email,
            "department_id": department_id,
            "manager_id": manager_id,
            "start_date": start_date,
            "base_salary": base_salary,
            "location": location,
            "role": role_enum,
            "status": "active",
            "tenure_months": tenure_months,
            "created_at": timestamp,
            "last_updated": timestamp,
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_worker",
                "description": "Create a new worker (employee) in the HR system. Requires full_name, email, and department_id. Optional: manager_id, start_date (YYYY-MM-DD format, defaults to 2025-12-12), base_salary (defaults to 0.0), location, role (defaults to 'worker' which maps to 'non_admin'). Returns created employee details including employee_id, full_name, email, department_id, manager_id, start_date, base_salary, location, role, status, tenure_months, created_at, and last_updated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "full_name": {
                            "type": "string",
                            "description": "Full name of the worker"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address of the worker (must be unique)"
                        },
                        "department_id": {
                            "type": "string",
                            "description": "Department ID where the worker will be assigned"
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "Manager ID (optional, must be an existing employee)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format (optional, defaults to 2025-12-12)"
                        },
                        "base_salary": {
                            "type": "number",
                            "description": "Base salary amount (optional, defaults to 0.0)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location of the worker (optional)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role of the worker (optional, defaults to 'worker' which maps to 'non_admin'). Use 'admin' for admin role."
                        }
                    },
                    "required": ["full_name", "email", "department_id"]
                }
            }
        }

