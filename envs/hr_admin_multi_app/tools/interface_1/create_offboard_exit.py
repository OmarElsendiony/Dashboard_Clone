import json
from datetime import datetime
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateOffboardExit(Tool):
    """
    Create a new employee exit case in the system to initiate offboarding.
    - Requires employee_id, reason, and exit_date.
    - Optionally accepts exit_clearance_status.
    - Validates that employee exists and is active.
    - Validates reason enum and exit_date format.
    - Auto-generates exit_case_id, created_at, and last_updated.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        reason: str,
        exit_date: str,
        exit_clearance_status: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "exit_case": {...}} on success
          {"success": False, "error": "..."} on error
        """

        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        exit_cases_dict = data.get("exit_cases", {})
        if not isinstance(exit_cases_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid exit_cases container: expected dict at data['exit_cases']",
                }
            )

        employees_dict = data.get("employees", {})
        if not isinstance(employees_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )

        # Validate required fields
        if employee_id is None:
            return json.dumps({"success": False, "error": "employee_id is required"})

        if reason is None or not reason.strip():
            return json.dumps(
                {
                    "success": False,
                    "error": "reason is required and cannot be empty",
                }
            )

        if exit_date is None or not exit_date.strip():
            return json.dumps(
                {
                    "success": False,
                    "error": "exit_date is required and cannot be empty",
                }
            )

        # Convert IDs to strings for consistent comparison
        employee_id_str = str(employee_id)

        # Validate employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        # Validate employee is active
        employee = employees_dict[employee_id_str]
        employee_status = employee.get("status", "").lower()
        if employee_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' is not active (status: {employee_status})",
                }
            )

        # Validate reason enum
        valid_reasons = [
            "voluntary_resignation",
            "layoff",
            "misconduct",
            "policy_violation",
        ]
        if reason not in valid_reasons:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid reason: '{reason}'. Must be one of {valid_reasons}",
                }
            )

        # Validate exit_date format (YYYY-MM-DD)
        try:
            # Parse the date to validate format
            parsed_date = datetime.strptime(exit_date, "%Y-%m-%d")
            # Convert to datetime string format to match DB storage (YYYY-MM-DDTHH:MM:SS)
            exit_date = parsed_date.strftime("%Y-%m-%dT00:00:00")
        except ValueError:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid exit_date format: '{exit_date}'. Must be YYYY-MM-DD format (e.g., '2024-12-31')",
                }
            )

        # Validate exit_clearance_status enum if provided
        valid_statuses = ["pending", "cleared"]
        if exit_clearance_status is not None:
            if exit_clearance_status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid exit_clearance_status: '{exit_clearance_status}'. Must be one of {valid_statuses}",
                    }
                )
        else:
            # Default status
            exit_clearance_status = "pending"

        # Check if employee already has an exit case
        for exit_case in exit_cases_dict.values():
            if exit_case.get("employee_id") == employee_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee with ID '{employee_id_str}' already has an exit case (exit_case_id: {exit_case.get('exit_case_id')})",
                    }
                )

        # Generate new exit_case_id (find max existing ID and add 1)
        if exit_cases_dict:
            try:
                max_id = max(int(eid) for eid in exit_cases_dict.keys())
                new_exit_case_id = str(max_id + 1)
            except (ValueError, TypeError):
                # If IDs are not numeric, use length + 1
                new_exit_case_id = str(len(exit_cases_dict) + 1)
        else:
            new_exit_case_id = "1"

        # Generate timestamps (use static date for consistency)
        current_time = "2025-11-16T23:59:00"

        # Create new exit case record
        new_exit_case = {
            "exit_case_id": new_exit_case_id,
            "employee_id": employee_id_str,
            "reason": reason,
            "exit_date": exit_date,
            "exit_clearance_status": exit_clearance_status,
            "created_at": current_time,
            "last_updated": current_time,
        }

        # Add to exit_cases dictionary
        exit_cases_dict[new_exit_case_id] = new_exit_case

        return json.dumps(
            {
                "success": True,
                "exit_case": new_exit_case,
                "message": f"Exit case {new_exit_case_id} created successfully for employee {employee_id_str}",
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
                "name": "create_offboard_exit",
                "description": "Creates a new employee exit case to initiate the offboarding process in the HR system. An exit case represents the formal start of an employee's departure from the organization, whether voluntary or involuntary. This tool is used when an employee resigns, is laid off, or is terminated due to misconduct or policy violations. The exit case tracks the reason for departure, exit date, and clearance status throughout the offboarding workflow. The employee must exist in the system and have an 'active' status to create an exit case. Each employee can only have one exit case at a time. The exit clearance status defaults to 'pending' and will be updated to 'cleared' once all exit procedures are completed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The unique identifier of the employee who is exiting. Must reference an existing employee with 'active' status in the system. ",
                        },
                        "reason": {
                            "type": "string",
                            "description": "The reason for the employee's departure. Must be one of: 'voluntary_resignation' (employee resigning voluntarily), 'layoff' (company-initiated separation due to restructuring or downsizing), 'misconduct' (termination due to employee misconduct), 'policy_violation' (termination due to violation of company policies). This is a required field.",
                        },
                        "exit_date": {
                            "type": "string",
                            "description": "The date when the employee will officially exit the organization. Must be in YYYY-MM-DD format (e.g., '2024-12-31'). This is the employee's last day of employment. This is a required field.",
                        },
                        "exit_clearance_status": {
                            "type": "string",
                            "description": "The clearance status of the exit case. Must be one of: 'pending' (exit procedures not yet completed, default), 'cleared' (all exit procedures completed and approved). If not provided, defaults to 'pending'. This status will be updated as the employee completes IT asset returns, finance settlements, and HR clearances.",
                        },
                    },
                    "required": ["employee_id", "reason", "exit_date"],
                },
            },
        }
