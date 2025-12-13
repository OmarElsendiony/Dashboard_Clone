import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ProcessPayrollInput(Tool):
    """
    Process (create or update) payroll input for an employee.
    Used to add new payroll inputs or update existing ones.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        input_id: Optional[str] = None,
        hours_worked: Optional[float] = None,
        overtime_hours: Optional[float] = None,
        status: Optional[str] = None,
        issue_field: Optional[str] = None,
        payroll_variance_percent: Optional[float] = None,
    ) -> str:
        """
        Process payroll input - create new or update existing.
        
        Args:
            data: Dictionary containing payroll_inputs, employees, and payroll_cycles
            employee_id: ID of the employee (required)
            cycle_id: ID of the payroll cycle (required)
            input_id: Optional input ID to update existing input
            hours_worked: Hours worked in the period
            overtime_hours: Overtime hours worked
            status: Status of the input ('pending' or 'review')
            issue_field: Issue description if any
            payroll_variance_percent: Variance percentage
            
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
        
        employees = data.get("employees", {})
        if not isinstance(employees, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )
        
        payroll_cycles = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
                }
            )
        
        # Validate required fields
        if not employee_id:
            return json.dumps(
                {"success": False, "error": "employee_id is required"}
            )
        
        if not cycle_id:
            return json.dumps(
                {"success": False, "error": "cycle_id is required"}
            )
        
        employee_id_str = str(employee_id)
        cycle_id_str = str(cycle_id)
        
        # Validate employee exists
        if employee_id_str not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )
        
        employee = employees[employee_id_str]
        
        # Validate cycle exists
        if cycle_id_str not in payroll_cycles:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                }
            )
        
        cycle = payroll_cycles[cycle_id_str]
        
        # Validate status if provided
        valid_statuses = ["pending", "review"]
        if status and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                }
            )
        
        timestamp = "2025-11-16T23:59:00"
        
        # UPDATE MODE: If input_id is provided
        if input_id:
            input_id_str = str(input_id)
            
            if input_id_str not in payroll_inputs:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payroll input with ID '{input_id_str}' not found",
                    }
                )
            
            payroll_input = payroll_inputs[input_id_str]
            
            # Check if cycle is closed
            if cycle.get("status") == "closed":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot update payroll input. Payroll cycle '{cycle_id_str}' is closed. Please escalate to Payroll Partner.",
                    }
                )
            
            # Update fields if provided
            if hours_worked is not None:
                try:
                    hours_worked_float = float(hours_worked)
                    if hours_worked_float < 0:
                        return json.dumps(
                            {"success": False, "error": "hours_worked must be non-negative"}
                        )
                    payroll_input["hours_worked"] = str(hours_worked_float)
                except (ValueError, TypeError):
                    return json.dumps(
                        {"success": False, "error": "hours_worked must be a valid number"}
                    )
            
            if overtime_hours is not None:
                try:
                    overtime_hours_float = float(overtime_hours)
                    if overtime_hours_float < 0:
                        return json.dumps(
                            {"success": False, "error": "overtime_hours must be non-negative"}
                        )
                    payroll_input["overtime_hours"] = str(overtime_hours_float)
                except (ValueError, TypeError):
                    return json.dumps(
                        {"success": False, "error": "overtime_hours must be a valid number"}
                    )
            
            if status:
                payroll_input["status"] = status
            
            if issue_field is not None:
                payroll_input["issue_field"] = issue_field
            
            if payroll_variance_percent is not None:
                try:
                    variance_float = float(payroll_variance_percent)
                    payroll_input["payroll_variance_percent"] = str(variance_float)
                except (ValueError, TypeError):
                    return json.dumps(
                        {"success": False, "error": "payroll_variance_percent must be a valid number"}
                    )
            
            # Recalculate gross_pay if hours changed
            if hours_worked is not None or overtime_hours is not None:
                base_salary = float(employee.get("base_salary", 0))
                # Assuming bi-weekly pay period (80 hours), calculate hourly rate
                hourly_rate = base_salary / 26 / 80  # 26 pay periods per year, 80 hours per period
                
                total_hours = float(payroll_input.get("hours_worked", 0))
                total_overtime = float(payroll_input.get("overtime_hours", 0))
                
                # Regular pay + overtime pay (typically 1.5x)
                gross_pay = (total_hours * hourly_rate) + (total_overtime * hourly_rate * 1.5)
                payroll_input["gross_pay"] = f"{gross_pay:.2f}"
            
            payroll_input["last_updated"] = timestamp
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Payroll input '{input_id_str}' has been updated successfully",
                    "payroll_input": payroll_input,
                    "action": "updated",
                }
            )
        
        # CREATE MODE: If input_id is not provided
        else:
            # Validate required fields for creation
            if hours_worked is None:
                return json.dumps(
                    {"success": False, "error": "hours_worked is required for creating a new payroll input"}
                )
            
            # Validate hours_worked
            try:
                hours_worked_float = float(hours_worked)
                if hours_worked_float < 0:
                    return json.dumps(
                        {"success": False, "error": "hours_worked must be non-negative"}
                    )
            except (ValueError, TypeError):
                return json.dumps(
                    {"success": False, "error": "hours_worked must be a valid number"}
                )
            
            # Validate overtime_hours
            if overtime_hours is None:
                overtime_hours_float = 0.0
            else:
                try:
                    overtime_hours_float = float(overtime_hours)
                    if overtime_hours_float < 0:
                        return json.dumps(
                            {"success": False, "error": "overtime_hours must be non-negative"}
                        )
                except (ValueError, TypeError):
                    return json.dumps(
                        {"success": False, "error": "overtime_hours must be a valid number"}
                    )
            
            # Check if payroll input already exists for this employee and cycle
            for existing_input in payroll_inputs.values():
                if (
                    existing_input.get("employee_id") == employee_id_str
                    and existing_input.get("cycle_id") == cycle_id_str
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Payroll input already exists for employee '{employee_id_str}' in cycle '{cycle_id_str}' (input_id: '{existing_input.get('input_id')}')",
                        }
                    )
            
            # Calculate gross_pay
            base_salary = float(employee.get("base_salary", 0))
            # Assuming bi-weekly pay period (80 hours), calculate hourly rate
            hourly_rate = base_salary / 26 / 80  # 26 pay periods per year, 80 hours per period
            
            # Regular pay + overtime pay (typically 1.5x)
            gross_pay = (hours_worked_float * hourly_rate) + (overtime_hours_float * hourly_rate * 1.5)
            
            # Generate new input ID
            def generate_input_id(inputs: Dict[str, Any]) -> str:
                if not inputs:
                    return "1"
                try:
                    max_id = max(int(k) for k in inputs.keys() if k.isdigit())
                    return str(max_id + 1)
                except ValueError:
                    return "1"
            
            new_input_id = generate_input_id(payroll_inputs)
            
            # Create new payroll input
            new_input = {
                "input_id": new_input_id,
                "employee_id": employee_id_str,
                "cycle_id": cycle_id_str,
                "hours_worked": str(hours_worked_float),
                "overtime_hours": str(overtime_hours_float),
                "gross_pay": f"{gross_pay:.2f}",
                "payroll_variance_percent": str(payroll_variance_percent) if payroll_variance_percent is not None else None,
                "status": status if status else "pending",
                "issue_field": issue_field,
                "created_at": timestamp,
                "last_updated": timestamp,
            }
            
            payroll_inputs[new_input_id] = new_input
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Payroll input has been created successfully for employee '{employee.get('full_name')}' ({employee_id_str}) in cycle '{cycle_id_str}'",
                    "payroll_input": new_input,
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
                "name": "process_payroll_input",
                "description": (
                    "Process (create or update) payroll input for an employee. "
                    "CREATE MODE: If input_id is not provided, creates a new payroll input. "
                    "Requires employee_id, cycle_id, and hours_worked. "
                    "Validates employee and cycle exist, and ensures no duplicate input for the same employee/cycle. "
                    "Automatically calculates gross_pay based on hours_worked, overtime_hours, and employee's base_salary. "
                    "UPDATE MODE: If input_id is provided, updates the existing payroll input. "
                    "Can update hours_worked, overtime_hours, status, issue_field, and payroll_variance_percent. "
                    "Validates that the payroll cycle is not closed before allowing updates. "
                    "If cycle is closed, returns an error to escalate to Payroll Partner."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (required)",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "ID of the payroll cycle (required)",
                        },
                        "input_id": {
                            "type": "string",
                            "description": "Optional: Input ID to update an existing payroll input. If provided, enters UPDATE mode.",
                        },
                        "hours_worked": {
                            "type": "number",
                            "description": "Hours worked in the period (required). For CREATE mode (when input_id is not provided), this must be provided to create the new payroll input. For UPDATE mode (when input_id is provided), this will update the hours_worked field.",
                        },
                        "overtime_hours": {
                            "type": "number",
                            "description": "Overtime hours worked (optional, defaults to 0)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the payroll input (optional, defaults to 'pending'). Valid values: 'pending', 'review'",
                            "enum": ["pending", "review"],
                        },
                        "issue_field": {
                            "type": "string",
                            "description": "Issue description if any (optional, e.g., 'variance exceeds 10%', 'requires manual verification')",
                        },
                        "payroll_variance_percent": {
                            "type": "number",
                            "description": "Variance percentage (optional)",
                        },
                    },
                    "required": ["employee_id", "cycle_id", "hours_worked"],
                },
            },
        }

