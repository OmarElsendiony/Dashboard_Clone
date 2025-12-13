import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetPayrollInput(Tool):
    """
    Retrieve payroll input records for a worker.
    Used to get payroll input data for validation, updates, and verification.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """
        Retrieve payroll input records for a specific employee and/or cycle.
        
        Args:
            data: Dictionary containing payroll_inputs and employees
            employee_id: ID of the employee (optional)
            cycle_id: ID of the payroll cycle (optional)
            email: Email address of the employee (optional)
            
        Returns:
            JSON string with success status and payroll input details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        payroll_inputs = data.get("payroll_inputs", {})
        if not isinstance(payroll_inputs, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_inputs container: expected dict at data['payroll_inputs']",
                }
            )
        
        # Validate that at least one identifier is provided
        if not employee_id and not cycle_id and not email:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one of employee_id, cycle_id, or email must be provided"
                }
            )
        
        # If email is provided, look up employee_id from employees
        resolved_employee_id = None
        if email:
            employees = data.get("employees", {})
            if not isinstance(employees, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid employees container: expected dict at data['employees']",
                    }
                )
            
            # Normalize the input email (lowercase and strip whitespace)
            normalized_email = str(email).strip().lower() if email else ""
            
            # Find employee by email (case-insensitive, whitespace-tolerant)
            found_employee_id = None
            for emp_id, employee in employees.items():
                employee_email = employee.get("email")
                if employee_email:
                    # Normalize stored email for comparison
                    normalized_employee_email = str(employee_email).strip().lower()
                    if normalized_employee_email == normalized_email:
                        found_employee_id = str(emp_id)
                        break
            
            if not found_employee_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"No employee found with email '{email}'",
                    }
                )
            
            resolved_employee_id = found_employee_id
        
        # Use provided employee_id or resolved from email
        if employee_id:
            resolved_employee_id = str(employee_id)
        
        # Find payroll inputs matching the criteria
        matching_inputs = []
        for payroll_input in payroll_inputs.values():
            match_employee = True
            match_cycle = True
            
            # Check employee_id match if provided
            if resolved_employee_id:
                if payroll_input.get("employee_id") != resolved_employee_id:
                    match_employee = False
            
            # Check cycle_id match if provided
            if cycle_id:
                cycle_id_str = str(cycle_id)
                if payroll_input.get("cycle_id") != cycle_id_str:
                    match_cycle = False
            
            # Add to results if both conditions match
            if match_employee and match_cycle:
                matching_inputs.append(payroll_input)
        
        # Return results
        if not matching_inputs:
            error_parts = []
            if resolved_employee_id:
                error_parts.append(f"employee '{resolved_employee_id}'")
            if cycle_id:
                error_parts.append(f"cycle '{cycle_id}'")
            if email:
                error_parts.append(f"email '{email}'")
            
            error_msg = f"No payroll input found for {', '.join(error_parts)}"
            return json.dumps(
                {
                    "success": False,
                    "error": error_msg,
                }
            )
        
        # Typically there should be only one payroll input per employee per cycle
        # But we return all matching records just in case
        if len(matching_inputs) == 1:
            return json.dumps(
                {
                    "success": True,
                    "payroll_input": matching_inputs[0],
                }
            )
        else:
            return json.dumps(
                {
                    "success": True,
                    "count": len(matching_inputs),
                    "payroll_inputs": matching_inputs,
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
                "name": "get_payroll_input",
                "description": (
                    "Retrieve payroll input records for a specific worker and/or cycle. "
                    "Used to get payroll input data for validation, updates, and verification. "
                    "Returns payroll input details including hours_worked, overtime_hours, "
                    "gross_pay, payroll_variance_percent, status, and issue_field. "
                    "Used in SOPs to retrieve payroll input records before updates, "
                    "validate if the payroll period is locked or closed, "
                    "and verify payroll input status during earning operations. "
                    "At least one of employee_id, cycle_id, or email must be provided."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": ["string", "null"],
                            "description": "ID of the employee (optional)",
                        },
                        "cycle_id": {
                            "type": ["string", "null"],
                            "description": "ID of the payroll cycle (optional)",
                        },
                        "email": {
                            "type": ["string", "null"],
                            "description": "Email address of the employee (optional). If provided, will be used to look up the employee_id.",
                        },
                    },
                    "required": [],
                },
            },
        }

