import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class InitiateTermination(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        reason: str,
        exit_date: str,
        exit_clearance_status: str = 'pending'
    ) -> str:
        """
        Creates an exit case for an employee termination.
        Validates employee exists and is active, and checks for existing exit case.
        """
        exit_cases = data.get("exit_cases", {})
        employees = data.get("employees", {})
        timestamp = "2025-12-12T12:00:00"
        
        # Validate required fields
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        if not reason:
            return json.dumps({
                "success": False,
                "error": "reason is required"
            })
        
        if not exit_date:
            return json.dumps({
                "success": False,
                "error": "exit_date is required"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        employee = employees[employee_id]
        
        # Validate employee is active (SOP 17)
        if employee.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"Employee '{employee_id}' is not active (status is '{employee.get('status')}'). Only active employees can have termination initiated."
            })
        
        # Check if exit case already exists for this employee (unique constraint)
        for exit_case_id, exit_case in exit_cases.items():
            if exit_case.get("employee_id") == employee_id:
                return json.dumps({
                    "success": False,
                    "error": f"An exit case already exists for employee_id '{employee_id}' (exit_case_id: '{exit_case_id}')"
                })
        
        # Validate reason enum
        valid_reasons = ["misconduct", "security_breach", "policy_violation", "voluntary_resignation", "layoff"]
        if reason not in valid_reasons:
            return json.dumps({
                "success": False,
                "error": f"Invalid reason. Must be one of: {', '.join(valid_reasons)}"
            })
        
        # Validate exit_clearance_status enum
        valid_clearance_statuses = ["pending", "cleared"]
        if exit_clearance_status not in valid_clearance_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid exit_clearance_status. Must be one of: {', '.join(valid_clearance_statuses)}"
            })
        
        # Generate new exit_case_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_exit_case_id = generate_id(exit_cases)
        
        # Create new exit case record
        new_exit_case = {
            "exit_case_id": new_exit_case_id,
            "employee_id": employee_id,
            "reason": reason,
            "exit_date": exit_date,
            "exit_clearance_status": exit_clearance_status,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        exit_cases[new_exit_case_id] = new_exit_case
        
        return json.dumps({
            "success": True,
            "exit_case": new_exit_case
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "initiate_termination",
                "description": "Creates an exit case for an employee termination. Validates employee exists and is active, and checks for existing exit case. Reason must be from offboarding_reason enum.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Offboarding reason: misconduct, security_breach, policy_violation, voluntary_resignation, layoff (required)",
                            "enum": ["misconduct", "security_breach", "policy_violation", "voluntary_resignation", "layoff"]
                        },
                        "exit_date": {
                            "type": "string",
                            "description": "Exit date (required)"
                        },
                        "exit_clearance_status": {
                            "type": "string",
                            "description": "Exit clearance status: pending, cleared (optional, default: 'pending')",
                            "enum": ["pending", "cleared"]
                        }
                    },
                    "required": ["employee_id", "reason", "exit_date"]
                }
            }
        }
