import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateEmployeeBenefitEnrollment(Tool):
    """
    Create a benefit enrollment for an employee.
    Accepts either employee_id or employee_email to identify the employee.
    Validates employee status and benefit plan before creating enrollment.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        plan_id: str,
        start_date: str,
        employee_id: Optional[str] = None,
        employee_email: Optional[str] = None,
    ) -> str:
        """
        Create enrollment for an employee in a benefit plan.
        
        Args:
            data: Dictionary containing employees, benefit_plans, and benefit_enrollments
            plan_id: ID of the benefit plan (required)
            start_date: Start date of enrollment in YYYY-MM-DD format (required)
            employee_id: ID of the employee to enroll (optional, but either employee_id or employee_email is required)
            employee_email: Email of the employee to enroll (optional, but either employee_id or employee_email is required)
            
        Returns:
            JSON string with success status and enrollment details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        employees = data.get("employees", {})
        if not isinstance(employees, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )
        
        benefit_plans = data.get("benefit_plans", {})
        if not isinstance(benefit_plans, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid benefit_plans container: expected dict at data['benefit_plans']",
                }
            )
        
        benefit_enrollments = data.get("benefit_enrollments", {})
        if not isinstance(benefit_enrollments, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid benefit_enrollments container: expected dict at data['benefit_enrollments']",
                }
            )
        
        # Validate required fields
        if not employee_id and not employee_email:
            return json.dumps(
                {"success": False, "error": "Either employee_id or employee_email is required"}
            )
        
        if not plan_id:
            return json.dumps(
                {"success": False, "error": "plan_id is required"}
            )
        
        if not start_date:
            return json.dumps(
                {"success": False, "error": "start_date is required"}
            )
        
        plan_id_str = str(plan_id)
        
        # Find employee by ID or email
        employee = None
        employee_id_str = None
        
        if employee_id:
            # Look up by employee_id
            employee_id_str = str(employee_id)
            if employee_id_str not in employees:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee with ID '{employee_id_str}' not found",
                    }
                )
            employee = employees[employee_id_str]
            
            # If both employee_id and employee_email are provided, validate they match
            if employee_email and employee.get("email") != employee_email:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee email mismatch. Provided email '{employee_email}' does not match the email '{employee.get('email')}' for employee ID '{employee_id_str}'",
                    }
                )
        else:
            # Look up by employee_email
            for emp_id, emp_data in employees.items():
                if emp_data.get("email") == employee_email:
                    employee = emp_data
                    employee_id_str = emp_id
                    break
            
            if not employee:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee with email '{employee_email}' not found",
                    }
                )
        
        # Validate employee status is active
        if employee.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee '{employee_id_str}' must have 'active' status. Current status: '{employee.get('status')}'",
                }
            )
        
        # Validate benefit plan exists
        if plan_id_str not in benefit_plans:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Benefit plan with ID '{plan_id_str}' not found",
                }
            )
        
        benefit_plan = benefit_plans[plan_id_str]
        
        # Validate benefit plan is active
        if benefit_plan.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Benefit plan '{plan_id_str}' must be 'active'. Current status: '{benefit_plan.get('status')}'",
                }
            )
        
        # Validate start_date format (basic YYYY-MM-DD check)
        try:
            if len(start_date) != 10 or start_date[4] != "-" or start_date[7] != "-":
                raise ValueError("Invalid date format")
            # Try to parse the date components
            year, month, day = start_date.split("-")
            year_int = int(year)
            month_int = int(month)
            day_int = int(day)
            if not (1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 1900):
                raise ValueError("Invalid date values")
        except (ValueError, AttributeError):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid start_date format. Expected YYYY-MM-DD, got: '{start_date}'",
                }
            )
        
        # Check for duplicate enrollment (employee_id, plan_id must be unique)
        for enrollment in benefit_enrollments.values():
            if (
                enrollment.get("employee_id") == employee_id_str
                and enrollment.get("plan_id") == plan_id_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Enrollment already exists for employee '{employee_id_str}' in plan '{plan_id_str}' (enrollment_id: '{enrollment.get('enrollment_id')}'). An employee can only be enrolled in the same plan once.",
                    }
                )
        
        # Generate new enrollment ID
        def generate_enrollment_id(enrollments: Dict[str, Any]) -> str:
            if not enrollments:
                return "1"
            try:
                max_id = max(int(k) for k in enrollments.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                return "1"
        
        new_enrollment_id = generate_enrollment_id(benefit_enrollments)
        timestamp = "2025-12-12T12:00:00"
        
        # Create new enrollment
        new_enrollment = {
            "enrollment_id": new_enrollment_id,
            "employee_id": employee_id_str,
            "plan_id": plan_id_str,
            "start_date": start_date,
            "is_active": True,
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        
        benefit_enrollments[new_enrollment_id] = new_enrollment
        
        return json.dumps(
            {
                "success": True,
                "message": f"Benefit enrollment created successfully for employee '{employee.get('full_name')}' ({employee_id_str}) in plan '{benefit_plan.get('name')}' ({plan_id_str})",
                "enrollment": new_enrollment,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "create_employee_benefit_enrollment",
                "description": (
                    "Create a benefit enrollment for an employee. "
                    "You must provide either employee_id or employee_email (or both) to identify the employee. "
                    "Validates that the employee exists and has 'active' status. "
                    "Verifies the benefit plan exists and is 'active'. "
                    "Ensures no duplicate enrollment exists (an employee can only be enrolled in the same plan once). "
                    "Returns the created enrollment details with auto-generated enrollment_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee to enroll (optional, but either employee_id or employee_email must be provided)",
                        },
                        "plan_id": {
                            "type": "string",
                            "description": "ID of the benefit plan (required)",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date of enrollment in YYYY-MM-DD format (required)",
                        },
                        "employee_email": {
                            "type": "string",
                            "description": "Email of the employee to enroll (optional, but either employee_id or employee_email must be provided)",
                        },
                    },
                    "required": ["plan_id", "start_date"],
                },
            },
        }

