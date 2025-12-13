import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class InitiateWorkerTermination(Tool):
    """
    Initiate worker termination by creating an exit case.
    Used to start the employee exit process.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        reason: str,
        exit_date: str,
    ) -> str:
        """
        Initiate worker termination by creating an exit case.
        
        Args:
            data: Dictionary containing exit_cases and employees
            employee_id: ID of the employee (required)
            reason: Reason for termination (required)
            exit_date: Date of exit (required, YYYY-MM-DD format)
            
        Returns:
            JSON string with success status and exit case details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        exit_cases = data.get("exit_cases", {})
        if not isinstance(exit_cases, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid exit_cases container: expected dict at data['exit_cases']",
                }
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
        
        if not reason:
            return json.dumps(
                {"success": False, "error": "reason is required"}
            )
        
        if not exit_date:
            return json.dumps(
                {"success": False, "error": "exit_date is required"}
            )
        
        employee_id_str = str(employee_id)
        
        # Validate employee exists
        if employee_id_str not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found. Halt and report the error.",
                }
            )
        
        employee = employees[employee_id_str]
        
        # Validate employee has active status
        if employee.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee '{employee_id_str}' does not have 'active' status. Current status: '{employee.get('status')}'. Halt and report the error.",
                }
            )
        
        # Validate reason
        valid_reasons = [
            "voluntary_resignation",
            "layoff",
            "misconduct",
            "policy_violation",
            "security_breach",
        ]
        if reason not in valid_reasons:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid reason value: '{reason}'. Must be one of {valid_reasons}",
                }
            )
        
        # Format exit_date to YYYY-MM-DD
        try:
            # Handle if exit_date is already a string in YYYY-MM-DD format
            if isinstance(exit_date, str):
                # Validate the format
                from datetime import datetime
                datetime.strptime(exit_date, "%Y-%m-%d")
                exit_date_str = exit_date
            else:
                # Convert date object to string
                exit_date_str = str(exit_date)
        except (ValueError, AttributeError):
            return json.dumps(
                {"success": False, "error": "exit_date must be in YYYY-MM-DD format"}
            )
        
        # Check if exit case already exists for this employee
        for existing_case in exit_cases.values():
            if existing_case.get("employee_id") == employee_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Exit case already exists for employee '{employee_id_str}' (exit_case_id: '{existing_case.get('exit_case_id')}')",
                    }
                )
        
        timestamp = "2025-12-12T12:00:00"
        
        # Generate new exit case ID
        def generate_exit_case_id(cases: Dict[str, Any]) -> str:
            if not cases:
                return "1"
            try:
                max_id = max(int(k) for k in cases.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                return "1"
        
        new_exit_case_id = generate_exit_case_id(exit_cases)
        
        # Create new exit case
        new_exit_case = {
            "exit_case_id": new_exit_case_id,
            "employee_id": employee_id_str,
            "reason": reason,
            "exit_date": exit_date_str,
            "exit_clearance_status": "pending",
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        
        exit_cases[new_exit_case_id] = new_exit_case
        
        # Update employee status to inactive
        employee["status"] = "inactive"
        employee["last_updated"] = timestamp
        
        return json.dumps(
            {
                "success": True,
                "message": f"Worker termination has been initiated for employee '{employee.get('full_name')}' ({employee_id_str}) with reason '{reason}' and exit date '{exit_date_str}'",
                "exit_case": new_exit_case,
                "employee_status_updated": "inactive",
                "action": "created",
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
                "name": "initiate_worker_termination",
                "description": (
                    "Initiate worker termination by creating an exit case. "
                    "Validates employee exists and has 'active' status. "
                    "Creates a new exit case record with the provided reason and exit date. "
                    "Automatically sets exit_clearance_status to 'pending'. "
                    "Updates employee status from 'active' to 'inactive'. "
                    "Prevents duplicate exit cases for the same employee. "
                    "Valid termination reasons: voluntary_resignation, layoff, misconduct, policy_violation, security_breach."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (required)",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for termination (required). Valid values: voluntary_resignation, layoff, misconduct, policy_violation, security_breach",
                            "enum": [
                                "voluntary_resignation",
                                "layoff",
                                "misconduct",
                                "policy_violation",
                                "security_breach",
                            ],
                        },
                        "exit_date": {
                            "type": "string",
                            "description": "Date of exit in YYYY-MM-DD format (required)",
                        },
                    },
                    "required": ["employee_id", "reason", "exit_date"],
                },
            },
        }

