import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateWorker(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
        manager_id: Optional[str] = None,
        department_id: Optional[str] = None,
        start_date: Optional[str] = None,
        tenure_months: Optional[int] = None,
        base_salary: Optional[float] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Update an existing worker (employee) record.
        Only provided fields will be updated.
        """
        employees = data.get("employees", {})
        departments = data.get("departments", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required parameter
        if not id:
            return json.dumps({
                "success": False,
                "error": "id is required"
            })
        
        # Validate employee exists
        if id not in employees:
            return json.dumps({
                "success": False,
                "error": f"Employee with ID '{id}' not found"
            })
        
        employee = employees[id]
        
        # Check if at least one field is being updated
        update_fields = [full_name, email, role, status, manager_id, department_id, 
                        start_date, tenure_months, base_salary, location]
        if all(field is None for field in update_fields):
            return json.dumps({
                "success": False,
                "error": "At least one field must be provided to update"
            })
        
        # Validate email uniqueness if email is being updated
        if email is not None:
            if email != employee.get("email"):
                for emp_id, emp in employees.items():
                    if emp_id != id and emp.get("email") == email:
                        return json.dumps({
                            "success": False,
                            "error": f"Email '{email}' already exists for employee_id '{emp_id}'"
                        })
        
        # Validate department if department_id is being updated
        if department_id is not None:
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
        
        # Validate manager if manager_id is being updated
        if manager_id is not None:
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
            
            # If department_id is also being updated, validate manager is in that department
            # Otherwise, validate manager is in the employee's current department
            target_dept_id = department_id if department_id is not None else employee.get("department_id")
            if manager.get("department_id") != target_dept_id:
                return json.dumps({
                    "success": False,
                    "error": f"Manager '{manager_id}' is not part of department '{target_dept_id}'"
                })
        
        # Validate role if provided
        if role is not None:
            valid_roles = ["admin", "non_admin"]
            if role not in valid_roles:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"
                })
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["active", "inactive", "on_leave", "probation"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Update fields
        if full_name is not None:
            employee["full_name"] = full_name
        if email is not None:
            employee["email"] = email
        if role is not None:
            employee["role"] = role
        if status is not None:
            employee["status"] = status
        if manager_id is not None:
            employee["manager_id"] = manager_id
        if department_id is not None:
            employee["department_id"] = department_id
        if start_date is not None:
            employee["start_date"] = start_date
        if tenure_months is not None:
            employee["tenure_months"] = tenure_months
        if base_salary is not None:
            employee["base_salary"] = str(base_salary)
        if location is not None:
            employee["location"] = location
        
        # Update timestamp
        employee["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "employee": employee
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_worker",
                "description": "Update an existing worker (employee) record. Only provided fields will be updated. Validates department and manager references.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Employee ID to update (required)"
                        },
                        "full_name": {
                            "type": "string",
                            "description": "Full name of the worker (optional)"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address of the worker (optional, must be unique)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role of the worker: admin, non_admin (optional)",
                            "enum": ["admin", "non_admin"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the worker: active, inactive, on_leave, probation (optional)",
                            "enum": ["active", "inactive", "on_leave", "probation"]
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "Manager employee ID (optional)"
                        },
                        "department_id": {
                            "type": "string",
                            "description": "Department ID (optional)"
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
                            "description": "Base salary (optional)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location (optional)"
                        }
                    },
                    "required": ["id"]
                }
            }
        }
