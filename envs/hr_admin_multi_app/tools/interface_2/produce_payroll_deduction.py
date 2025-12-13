import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ProducePayrollDeduction(Tool):
    """
    Create a new payroll deduction for an employee.
    Used to create new deductions when they don't already exist.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        deduction_rule_id: str,
        amount: float,
        deduction_date: str,
        cycle_id: Optional[str] = None,
        deduction_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Create a new payroll deduction for an employee.
        
        Args:
            data: Dictionary containing deductions, deduction_rules, employees, and payroll_cycles
            employee_id: ID of the employee (required)
            deduction_rule_id: ID of the deduction rule (required)
            amount: Deduction amount (required)
            deduction_date: Date of the deduction (required)
            cycle_id: Optional payroll cycle ID
            deduction_id: Optional deduction ID (not used in creation, for consistency with interface)
            status: Status of the deduction ('valid', 'invalid_limit_exceeded')
            
        Returns:
            JSON string with success status and deduction details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        deductions = data.get("deductions", {})
        if not isinstance(deductions, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid deductions container: expected dict at data['deductions']",
                }
            )
        
        deduction_rules = data.get("deduction_rules", {})
        if not isinstance(deduction_rules, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid deduction_rules container: expected dict at data['deduction_rules']",
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
        
        if not deduction_rule_id:
            return json.dumps(
                {"success": False, "error": "deduction_rule_id is required"}
            )
        
        if amount is None:
            return json.dumps(
                {"success": False, "error": "amount is required"}
            )
        
        if not deduction_date:
            return json.dumps(
                {"success": False, "error": "deduction_date is required"}
            )
        
        # Format deduction_date to YYYY-MM-DD
        try:
            # Handle if deduction_date is already a string in YYYY-MM-DD format
            if isinstance(deduction_date, str):
                # Validate the format
                from datetime import datetime
                datetime.strptime(deduction_date, "%Y-%m-%d")
                deduction_date_str = deduction_date
            else:
                # Convert date object to string
                deduction_date_str = str(deduction_date)
        except (ValueError, AttributeError):
            return json.dumps(
                {"success": False, "error": "deduction_date must be in YYYY-MM-DD format"}
            )
        
        employee_id_str = str(employee_id)
        deduction_rule_id_str = str(deduction_rule_id)
        
        # Validate employee exists
        if employee_id_str not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )
        
        employee = employees[employee_id_str]
        
        # Validate employee is active
        if employee.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee '{employee_id_str}' must have 'active' status. Current status: '{employee.get('status')}'",
                }
            )
        
        # Validate deduction rule exists
        if deduction_rule_id_str not in deduction_rules:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Deduction rule with ID '{deduction_rule_id_str}' not found. Halt condition applied.",
                }
            )
        
        deduction_rule = deduction_rules[deduction_rule_id_str]
        
        # Validate deduction rule is active
        if deduction_rule.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Deduction rule '{deduction_rule_id_str}' must have 'active' status. Current status: '{deduction_rule.get('status')}'",
                }
            )
        
        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float < 0:
                return json.dumps(
                    {"success": False, "error": "amount must be non-negative"}
                )
        except (ValueError, TypeError):
            return json.dumps(
                {"success": False, "error": "amount must be a valid number"}
            )
        
        # Validate cycle_id if provided
        if cycle_id:
            cycle_id_str = str(cycle_id)
            if cycle_id_str not in payroll_cycles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                    }
                )
        
        # Valid statuses
        valid_statuses = ["valid", "invalid_limit_exceeded"]
        
        # Validate status if provided
        if status and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                }
            )
        
        timestamp = "2025-11-16T23:59:00"
        
        # Check if deduction already exists for this employee, cycle, and rule
        if cycle_id:
            cycle_id_str = str(cycle_id)
            for existing_deduction in deductions.values():
                if (
                    existing_deduction.get("employee_id") == employee_id_str
                    and existing_deduction.get("cycle_id") == cycle_id_str
                    and existing_deduction.get("deduction_rule_id") == deduction_rule_id_str
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Deduction already exists for employee '{employee_id_str}', cycle '{cycle_id_str}', and rule '{deduction_rule_id_str}' (deduction_id: '{existing_deduction.get('deduction_id')}')",
                        }
                    )
        
        # Generate new deduction ID
        def generate_deduction_id(deductions_dict: Dict[str, Any]) -> str:
            if not deductions_dict:
                return "1"
            try:
                max_id = max(int(k) for k in deductions_dict.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                return "1"
        
        new_deduction_id = generate_deduction_id(deductions)
        
        # Create new deduction
        new_deduction = {
            "deduction_id": new_deduction_id,
            "employee_id": employee_id_str,
            "cycle_id": str(cycle_id) if cycle_id else None,
            "deduction_rule_id": deduction_rule_id_str,
            "amount": str(amount_float),
            "deduction_date": deduction_date_str,
            "status": status if status else "valid",
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        
        deductions[new_deduction_id] = new_deduction
        
        return json.dumps(
            {
                "success": True,
                "message": f"Payroll deduction has been created successfully for employee '{employee.get('full_name')}' ({employee_id_str}) with deduction type '{deduction_rule.get('deduction_type')}'",
                "deduction": new_deduction,
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
                "name": "produce_payroll_deduction",
                "description": (
                    "Create a new payroll deduction for an employee. "
                    "This tool is used when the deduction does not already exist. "
                    "Requires employee_id, deduction_rule_id, amount, and deduction_date. "
                    "Validates employee exists and has 'active' status. "
                    "Validates deduction rule exists and has 'active' status. "
                    "Prevents duplicate deductions for the same employee, cycle, and rule combination. "
                    "Automatically generates a new deduction_id for the created deduction."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (required)",
                        },
                        "deduction_rule_id": {
                            "type": "string",
                            "description": "ID of the deduction rule (required). Must be an active rule.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "Deduction amount (required, must be non-negative)",
                        },
                        "deduction_date": {
                            "type": "string",
                            "description": "Date of the deduction in YYYY-MM-DD format (required)",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional: ID of the payroll cycle",
                        },
                        "deduction_id": {
                            "type": "string",
                            "description": "Optional: Not used in creation but included for interface consistency",
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the deduction (optional, defaults to 'valid'). Valid values: 'valid', 'invalid_limit_exceeded'",
                            "enum": ["valid", "invalid_limit_exceeded"],
                        },
                    },
                    "required": ["employee_id", "deduction_rule_id", "amount", "deduction_date"],
                },
            },
        }

