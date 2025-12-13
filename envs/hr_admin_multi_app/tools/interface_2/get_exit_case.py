import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetExitCase(Tool):
    """
    Retrieve exit case details for an employee.
    Used to get information about an employee's exit case.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        exit_case_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        reason: Optional[str] = None,
        exit_clearance_status: Optional[str] = None,
    ) -> str:
        """
        Retrieve exit case details with flexible filtering options.
        
        All parameters are optional. If exit_case_id is provided, returns that specific exit case.
        Otherwise, filters exit cases based on provided criteria (employee_id, reason, exit_clearance_status).
        If no parameters are provided, returns all exit cases.
        
        Args:
            data: Dictionary containing exit_cases and employees
            exit_case_id: ID of the exit case (optional)
            employee_id: ID of the employee (optional)
            reason: Filter by termination reason (optional)
            exit_clearance_status: Filter by clearance status - "pending" or "cleared" (optional)
            
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
        
        # Validate reason if provided
        if reason is not None:
            valid_reasons = ["misconduct", "security_breach", "policy_violation", "voluntary_resignation", "layoff"]
            if reason not in valid_reasons:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid reason: '{reason}'. Must be one of {valid_reasons}",
                    }
                )
        
        # Validate exit_clearance_status if provided
        if exit_clearance_status is not None:
            valid_statuses = ["pending", "cleared"]
            if exit_clearance_status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid exit_clearance_status: '{exit_clearance_status}'. Must be one of {valid_statuses}",
                    }
                )
        
        # If exit_case_id is provided, retrieve that specific exit case
        if exit_case_id is not None:
            exit_case_id_str = str(exit_case_id)
            
            if exit_case_id_str not in exit_cases:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Exit case with ID '{exit_case_id_str}' not found",
                    }
                )
            
            exit_case = exit_cases[exit_case_id_str]
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Retrieved exit case '{exit_case_id_str}' for employee '{exit_case.get('employee_id')}' with reason '{exit_case.get('reason')}' and status '{exit_case.get('exit_clearance_status')}'",
                    "exit_case": exit_case,
                }
            )
        
        # Otherwise, filter exit cases based on provided criteria
        filtered_cases = []
        
        for case in exit_cases.values():
            # Apply employee_id filter
            if employee_id is not None:
                if case.get("employee_id") != str(employee_id):
                    continue
            
            # Apply reason filter
            if reason is not None:
                if case.get("reason") != reason:
                    continue
            
            # Apply exit_clearance_status filter
            if exit_clearance_status is not None:
                if case.get("exit_clearance_status") != exit_clearance_status:
                    continue
            
            filtered_cases.append(case)
        
        if not filtered_cases:
            return json.dumps(
                {
                    "success": False,
                    "error": "No exit cases found matching the specified criteria",
                }
            )
        
        return json.dumps(
            {
                "success": True,
                "message": f"Retrieved {len(filtered_cases)} exit case(s) matching the criteria",
                "exit_cases": filtered_cases,
                "count": len(filtered_cases),
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
                "name": "get_exit_case",
                "description": (
                    "Retrieve exit case details with flexible filtering options. "
                    "All parameters are optional. If exit_case_id is provided, returns that specific exit case. "
                    "Otherwise, filters exit cases based on any combination of: employee_id, reason, exit_clearance_status. "
                    "If no parameters are provided, returns all exit cases. "
                    "Returns exit case records including exit_case_id, employee_id, reason, "
                    "exit_date, exit_clearance_status, created_at, and last_updated. "
                    "This is typically used to check the clearance status and details before "
                    "processing exit clearance or settlement. "
                    "Valid exit clearance statuses: 'pending', 'cleared'. "
                    "Valid termination reasons: voluntary_resignation, layoff, misconduct, policy_violation, security_breach."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exit_case_id": {
                            "type": "string",
                            "description": "ID of the exit case (optional). If provided, returns that specific exit case.",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Filter by employee ID (optional). Returns exit case for the specified employee.",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Filter by termination reason (optional). Valid values: 'misconduct', 'security_breach', 'policy_violation', 'voluntary_resignation', 'layoff'.",
                            "enum": ["misconduct", "security_breach", "policy_violation", "voluntary_resignation", "layoff"],
                        },
                        "exit_clearance_status": {
                            "type": "string",
                            "description": "Filter by clearance status (optional). Valid values: 'pending', 'cleared'.",
                            "enum": ["pending", "cleared"],
                        },
                    },
                    "required": [],
                },
            },
        }

