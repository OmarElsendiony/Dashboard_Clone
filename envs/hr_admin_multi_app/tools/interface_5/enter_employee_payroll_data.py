
import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class EnterEmployeePayrollData(Tool):
    """
    Create new payroll input data for an employee.
    - Creates payroll input for an employee in a specific cycle.
    - Records hours worked and overtime hours.
    - Validates employee exists, cycle exists, and no duplicate input exists.
    - Sets initial status as 'pending'.
    - Returns the created payroll input details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        hours_worked: float,
        overtime_hours: Optional[float] = 0.0,
        input_status: Optional[str] = "pending",
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payroll_input": {...}} on success
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

        employees_dict = data.get("employees", {})
        if not isinstance(employees_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )

        payroll_cycles_dict = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
                }
            )

        payroll_inputs_dict = data.get("payroll_inputs", {})
        if not isinstance(payroll_inputs_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_inputs container: expected dict at data['payroll_inputs']",
                }
            )
        
        valid_payroll_statuses = {"pending", "approved", "cancelled", "locked"}
        if input_status not in valid_payroll_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid input_status '{input_status}'. Must be one of {valid_payroll_statuses}",
                }
            )

        # Validate required parameters
        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})
        
        if not cycle_id:
            return json.dumps({"success": False, "error": "cycle_id is required"})
        
        if hours_worked is None:
            return json.dumps({"success": False, "error": "hours_worked is required"})

        # Convert IDs to strings for consistent comparison
        employee_id_str = str(employee_id)
        cycle_id_str = str(cycle_id)

        # Check if employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        # Check if cycle exists
        if cycle_id_str not in payroll_cycles_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                }
            )

        # Validate numeric values
        try:
            hours_worked = float(hours_worked)
            overtime_hours = float(overtime_hours)
            
            if hours_worked < 0:
                return json.dumps(
                    {
                        "success": False,
                        "error": "hours_worked cannot be negative",
                    }
                )
            
            if overtime_hours < 0:
                return json.dumps(
                    {
                        "success": False,
                        "error": "overtime_hours cannot be negative",
                    }
                )
        except (ValueError, TypeError) as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid numeric value: {str(e)}",
                }
            )

        # Check if payroll input already exists for this employee and cycle
        for input_id, payroll_input in payroll_inputs_dict.items():
            if not isinstance(payroll_input, dict):
                continue
            
            if (str(payroll_input.get("employee_id")) == employee_id_str and 
                str(payroll_input.get("cycle_id")) == cycle_id_str):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payroll input already exists for employee '{employee_id_str}' in cycle '{cycle_id_str}' (input_id: {input_id}). Use update_employee_payroll_data to modify it.",
                    }
                )

        # Generate new input_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_input_id = generate_id(payroll_inputs_dict)

        timestamp = "2025-11-16T23:59:00"

        # Create new payroll input
        new_input = {
            "input_id": new_input_id,
            "employee_id": employee_id_str,
            "cycle_id": cycle_id_str,
            "hours_worked": hours_worked,
            "overtime_hours": overtime_hours,
            "payroll_variance_percent": None,
            "status": input_status,
            "issue_field": None,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        # Add to data
        payroll_inputs_dict[new_input_id] = new_input

        return json.dumps(
            {
                "success": True,
                "payroll_input": new_input,
                "message": f"Payroll input created successfully with ID: {new_input_id}",
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
                "name": "enter_employee_payroll_data",
                "description": (
                    "Create new payroll input data for an employee in a specific payroll cycle. "
                    "Validates that employee and cycle exist and that no duplicate payroll input "
                    "exists for the same employee-cycle combination. "
                    "Sets initial status as 'pending'. "
                    "Returns the created payroll input details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee to create payroll data for.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "The ID of the payroll cycle.",
                        },
                        "hours_worked": {
                            "type": "number",
                            "description": "Total regular hours worked by the employee. Must be non-negative.",
                        },
                        "overtime_hours": {
                            "type": "number",
                            "description": "Overtime hours worked by the employee. Defaults to 0 if not provided. Must be non-negative.",
                        },
                        "input_status": {
                            "type": "string",
                            "description": "Optional. Initial status of the payroll input. Defaults to 'pending'. Must be one of 'pending', 'approved', 'cancelled', or 'locked'.",
                        }
                    },
                    "required": ["employee_id", "cycle_id", "hours_worked"],
                },
            },
        }