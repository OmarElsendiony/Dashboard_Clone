import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateNewWorker(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        full_name: str,
        email: str,
        role: str,
        department_id: str,
        status: str = 'active',
        manager_id: Optional[str] = None,
        start_date: Optional[str] = None,
        tenure_months: Optional[int] = None,
        base_salary: Optional[float] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Create a new worker (employee) record.
        """
        employees = data.get("employees", {})
        departments = data.get("departments", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required fields
        if not full_name:
            return json.dumps({
                "success": False,
                "error": "full_name is required"
            })
        
        if not email:
            return json.dumps({
                "success": False,
                "error": "email is required"
            })
        
        if not role:
            return json.dumps({
                "success": False,
                "error": "role is required"
            })
        
        if not department_id:
            return json.dumps({
                "success": False,
                "error": "department_id is required"
            })
        
        # Validate email uniqueness
        for emp_id, employee in employees.items():
            if employee.get("email") == email:
                return json.dumps({
                    "success": False,
                    "error": f"Email '{email}' already exists for employee_id '{emp_id}'"
                })
        
        # Validate department exists and is active
        if department_id not in departments:
            return json.dumps({
                "success": False,
                "error": f"department_id '{department_id}' does not reference a valid department"
            })
        
        department = departments[department_id]
        if department.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"Department '{department_id}' is not active"
            })
        
        # Validate manager if provided
        if manager_id:
            if manager_id not in employees:
                return json.dumps({
                    "success": False,
                    "error": f"manager_id '{manager_id}' does not reference a valid employee"
                })
            
            manager = employees[manager_id]
            if manager.get("status") != "active":
                return json.dumps({
                    "success": False,
                    "error": f"Manager '{manager_id}' is not active"
                })
            
            # Validate manager is in the target department
            if manager.get("department_id") != department_id:
                return json.dumps({
                    "success": False,
                    "error": f"Manager '{manager_id}' is not part of department '{department_id}'"
                })
        
        # Validate role
        valid_roles = ["admin", "non_admin"]
        if role not in valid_roles:
            return json.dumps({
                "success": False,
                "error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            })
        
        # Validate status
        valid_statuses = ["active", "inactive", "on_leave", "probation"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Generate new employee_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_employee_id = generate_id(employees)
        
        # Set default start_date if not provided
        if not start_date:
            start_date = "2025-12-12"  # Use date part of timestamp
        
        # Set default base_salary if not provided (required in schema)
        if base_salary is None:
            base_salary = 0.0
        
        # Create new employee record
        new_employee = {
            "employee_id": new_employee_id,
            "manager_id": manager_id,
            "department_id": department_id,
            "start_date": start_date,
            "full_name": full_name,
            "email": email,
            "status": status,
            "tenure_months": tenure_months if tenure_months is not None else 0,
            "performance_rating": None,
            "base_salary": str(base_salary),
            "location": location,
            "role": role,
            "flag_financial_counseling_recommended": False,
            "flag_potential_overtime_violation": False,
            "flag_requires_payroll_review": False,
            "flag_high_offboard_risk": False,
            "flag_pending_settlement": False,
            "flag_requires_finance_approval": False,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        employees[new_employee_id] = new_employee
        
        return json.dumps({
            "success": True,
            "employee": new_employee
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_worker",
                "description": "Create a new worker (employee) record. Validates department and manager references, ensures email uniqueness.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "full_name": {
                            "type": "string",
                            "description": "Full name of the worker (required)"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address of the worker (required, must be unique)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role of the worker: admin, non_admin (required)",
                            "enum": ["admin", "non_admin"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the worker: active, inactive, on_leave, probation (optional, default: 'active')",
                            "enum": ["active", "inactive", "on_leave", "probation"]
                        },
                        "department_id": {
                            "type": "string",
                            "description": "Department ID (required)"
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "Manager employee ID (optional)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format (optional)"
                        },
                        "tenure_months": {
                            "type": "integer",
                            "description": "Tenure in months (optional)"
                        },
                        "base_salary": {
                            "type": "number",
                            "description": "Base salary (optional, defaults to 0.0)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location (optional)"
                        }
                    },
                    "required": ["full_name", "email", "role", "department_id"]
                }
            }
        }
