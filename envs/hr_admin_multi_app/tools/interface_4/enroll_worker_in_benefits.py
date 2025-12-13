import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class EnrollWorkerInBenefits(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        plan_id: str,
        start_date: str,
        is_active: bool = True
    ) -> str:
        """
        Enroll a worker (employee) in a benefit plan.
        """
        benefit_enrollments = data.get("benefit_enrollments", {})
        employees = data.get("employees", {})
        benefit_plans = data.get("benefit_plans", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required fields
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        if not plan_id:
            return json.dumps({
                "success": False,
                "error": "plan_id is required"
            })
        
        if not start_date:
            return json.dumps({
                "success": False,
                "error": "start_date is required"
            })
        
        # Validate employee exists and is active
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        employee = employees[employee_id]
        if employee.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"Employee '{employee_id}' is not active (status is '{employee.get('status')}')"
            })
        
        # Validate plan exists and is active
        if plan_id not in benefit_plans:
            return json.dumps({
                "success": False,
                "error": f"plan_id '{plan_id}' does not reference a valid benefit plan"
            })
        
        plan = benefit_plans[plan_id]
        if plan.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"Benefit plan '{plan_id}' is not active (status is '{plan.get('status')}')"
            })
        
        # Validate enrollment_window is open
        enrollment_window = plan.get("enrollment_window")
        if enrollment_window != "open":
            return json.dumps({
                "success": False,
                "error": f"Benefit plan '{plan_id}' enrollment window is '{enrollment_window}'. Enrollment is only allowed when enrollment_window is 'open'."
            })
        
        # Validate there is no existing enrollment for this employee+plan combination
        for enrollment_id, enrollment in benefit_enrollments.items():
            if enrollment.get("employee_id") == employee_id and enrollment.get("plan_id") == plan_id:
                return json.dumps({
                    "success": False,
                    "error": f"Employee '{employee_id}' is already enrolled in plan '{plan_id}' (enrollment_id: '{enrollment_id}')"
                })
        
        # Generate new enrollment_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_enrollment_id = generate_id(benefit_enrollments)
        
        # Create new enrollment record
        new_enrollment = {
            "enrollment_id": new_enrollment_id,
            "employee_id": employee_id,
            "plan_id": plan_id,
            "start_date": start_date,
            "is_active": is_active,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        benefit_enrollments[new_enrollment_id] = new_enrollment
        
        return json.dumps({
            "success": True,
            "enrollment": new_enrollment
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "enroll_worker_in_benefits",
                "description": "Enroll a worker (employee) in a benefit plan. Validates employee and plan exist and are active, enrollment_window is 'open', and checks for existing enrollment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "plan_id": {
                            "type": "string",
                            "description": "Benefit plan ID (required)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format (required)"
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "Whether the enrollment is active (optional, default: true)"
                        }
                    },
                    "required": ["employee_id", "plan_id", "start_date"]
                }
            }
        }
