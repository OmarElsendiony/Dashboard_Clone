import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class CreateBenefitEnrollment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        plan_id: str,
        start_date: str,
    ) -> str:
        """
        Create a new benefit enrollment for an employee.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee (required).
            plan_id: The ID of the benefit plan (required).
            start_date: The enrollment start date in format (YYYY-MM-DD) (required).
        
        Returns:
            JSON string with the created benefit enrollment record.
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

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})
        if not plan_id:
            return json.dumps({"error": "Missing required parameter: plan_id is required"})
        if not start_date:
            return json.dumps({"error": "Missing required parameter: start_date is required"})

        employee_id = str(employee_id)
        plan_id = str(plan_id)

        employees = data.get("employees", {})
        benefit_plans = data.get("benefit_plans", {})
        benefit_enrollments = data.get("benefit_enrollments", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        if plan_id not in benefit_plans:
            return json.dumps({"error": f"Benefit plan with ID '{plan_id}' not found"})

        plan = benefit_plans[plan_id]
        if plan.get("status") == "inactive":
            return json.dumps({"error": f"Cannot enroll in inactive benefit plan '{plan_id}'"})

        # Check for existing active enrollment
        for enrollment_id, enrollment in benefit_enrollments.items():
            if (enrollment.get("employee_id") == employee_id and 
                enrollment.get("plan_id") == plan_id and 
                enrollment.get("is_active")):
                return json.dumps({
                    "error": f"Employee '{employee_id}' already has an active enrollment in plan '{plan_id}'"
                })

        # Generate new enrollment ID
        enrollment_id = generate_id(benefit_enrollments)

        # Create benefit enrollment record
        timestamp = "2025-11-16T23:59:00"
        new_enrollment = {
            "enrollment_id": enrollment_id,
            "employee_id": employee_id,
            "plan_id": plan_id,
            "start_date": start_date,
            "is_active": True,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        benefit_enrollments[enrollment_id] = new_enrollment
        data["benefit_enrollments"] = benefit_enrollments

        return json.dumps(new_enrollment)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_benefit_enrollment",
                "description": (
                    "Creates a new benefit enrollment for an employee in a specific plan. "
                    "The plan must be active. An employee can only have one active enrollment per plan."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee (required).",
                        },
                        "plan_id": {
                            "type": "string",
                            "description": "The ID of the benefit plan (required).",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "The enrollment start date in format (YYYY-MM-DD) (required).",
                        },
                    },
                    "required": ["employee_id", "plan_id", "start_date"],
                },
            },
        }
