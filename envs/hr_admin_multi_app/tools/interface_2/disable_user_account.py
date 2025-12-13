import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class DisableUserAccount(Tool):
    """
    Disable user account and deactivate worker eligibility and system access.
    Updates employee status to 'inactive'.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Disable user account for an employee.
        
        Args:
            data: Dictionary containing employees
            employee_id: ID of the employee to deactivate (required)
            email: Email of the employee (optional, for validation)
            full_name: Full name of the employee (optional, for validation)
            status: Current status of the employee (optional, for validation)
            
        Returns:
            JSON string with success status and updated employee details
        """
        
        timestamp = "2025-12-12T12:00:00"
        
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
        
        # Validate required fields
        if not employee_id:
            return json.dumps(
                {"success": False, "error": "employee_id is required"}
            )
        
        employee_id_str = str(employee_id)
        
        # Validate employee exists
        if employee_id_str not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )
        
        employee = employees[employee_id_str]
        
        # Optional validation: check if provided email matches
        if email is not None:
            if employee.get("email") != email:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Email mismatch: employee '{employee_id_str}' has email '{employee.get('email')}', not '{email}'",
                    }
                )
        
        # Optional validation: check if provided full_name matches
        if full_name is not None:
            if employee.get("full_name") != full_name:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Full name mismatch: employee '{employee_id_str}' has name '{employee.get('full_name')}', not '{full_name}'",
                    }
                )
        
        # Optional validation: check if provided status matches
        if status is not None:
            if employee.get("status") != status:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Status mismatch: employee '{employee_id_str}' has status '{employee.get('status')}', not '{status}'",
                    }
                )
        
        old_status = employee.get("status")
        
        # Check if employee is already inactive
        if old_status == "inactive":
            return json.dumps(
                {
                    "success": True,
                    "message": f"Employee '{employee.get('full_name')}' ({employee_id_str}) is already inactive. No changes made.",
                    "employee": employee,
                    "previous_status": old_status,
                    "current_status": "inactive",
                    "already_inactive": True,
                }
            )
        
        # Update employee status to inactive
        employee["status"] = "inactive"
        employee["last_updated"] = timestamp
        
        return json.dumps(
            {
                "success": True,
                "message": f"User account disabled for employee '{employee.get('full_name')}' ({employee_id_str}). "
                          f"Status updated from '{old_status}' to 'inactive'. "
                          f"Worker eligibility and system access have been deactivated.",
                "employee": employee,
                "previous_status": old_status,
                "current_status": "inactive",
                "already_inactive": False,
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
                "name": "disable_user_account",
                "description": (
                    "Disable user account and deactivate worker eligibility and system access. "
                    "Updates the employee status to 'inactive', effectively removing their access to systems "
                    "and marking them as no longer active in the organization. "
                    "Requires employee_id. Optional parameters (email, full_name, status) can be provided for validation. "
                    "If employee is already inactive, returns success without making changes. "
                    "This is typically used during the exit settlement process after final payment has been processed. "
                    "Part of the employee offboarding workflow: after exit clearance is completed, settlement is paid, "
                    "the employee account is disabled, employment contract is terminated, and exit documents are archived. "
                    "Valid employee statuses: 'active', 'inactive', 'on_leave', 'probation'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee to deactivate (required)",
                        },
                        "email": {
                            "type": "string",
                            "description": "Email of the employee (optional, for validation). If provided, validates that this email matches the employee record.",
                        },
                        "full_name": {
                            "type": "string",
                            "description": "Full name of the employee (optional, for validation). If provided, validates that this name matches the employee record.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Expected current status of the employee (optional, for validation). If provided, validates that this status matches before deactivation. Valid values: 'active', 'inactive', 'on_leave', 'probation'.",
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }

