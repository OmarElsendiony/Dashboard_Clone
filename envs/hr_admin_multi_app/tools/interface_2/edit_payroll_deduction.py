import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class EditPayrollDeduction(Tool):
    """
    Edit (update) an existing payroll deduction.
    This tool is for UPDATING deductions only, not creating them.
    deduction_id is required to identify which deduction to update.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        deduction_id: str,
        employee_id: Optional[str] = None,
        deduction_rule_id: Optional[str] = None,
        amount: Optional[float] = None,
        deduction_date: Optional[str] = None,
        cycle_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Edit (update) an existing payroll deduction.
        Only provided fields will be updated; unprovided fields remain unchanged.
        
        Args:
            data: Dictionary containing deductions, deduction_rules, employees, and payroll_cycles
            deduction_id: ID of the deduction to update (REQUIRED)
            employee_id: Optional: Update employee ID
            deduction_rule_id: Optional: Update deduction rule ID
            amount: Optional: Update deduction amount
            deduction_date: Optional: Update date of the deduction
            cycle_id: Optional: Update payroll cycle ID
            status: Optional: Update status ('valid', 'invalid_limit_exceeded')
            
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
        
        # Validate required field - deduction_id
        if not deduction_id:
            return json.dumps(
                {"success": False, "error": "deduction_id is required"}
            )
        
        deduction_id_str = str(deduction_id)
        
        # Check if deduction exists
        if deduction_id_str not in deductions:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Deduction with ID '{deduction_id_str}' not found",
                }
            )
        
        deduction = deductions[deduction_id_str]
        
        # Validate optional fields only if provided
        
        # Validate employee_id if provided
        if employee_id is not None:
            employee_id_str = str(employee_id)
            if employee_id_str not in employees:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee with ID '{employee_id_str}' not found",
                    }
                )
            employee = employees[employee_id_str]
            if employee.get("status") != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee '{employee_id_str}' must have 'active' status. Current status: '{employee.get('status')}'",
                    }
                )
        
        # Validate deduction_rule_id if provided
        if deduction_rule_id is not None:
            deduction_rule_id_str = str(deduction_rule_id)
            if deduction_rule_id_str not in deduction_rules:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Deduction rule with ID '{deduction_rule_id_str}' not found. Halt condition applied.",
                    }
                )
            deduction_rule = deduction_rules[deduction_rule_id_str]
            if deduction_rule.get("status") != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Deduction rule '{deduction_rule_id_str}' must have 'active' status. Current status: '{deduction_rule.get('status')}'",
                    }
                )
        
        # Validate amount if provided
        if amount is not None:
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
        
        # Validate deduction_date if provided
        if deduction_date is not None:
            try:
                if isinstance(deduction_date, str):
                    from datetime import datetime
                    datetime.strptime(deduction_date, "%Y-%m-%d")
                    deduction_date_str = deduction_date
                else:
                    deduction_date_str = str(deduction_date)
            except (ValueError, AttributeError):
                return json.dumps(
                    {"success": False, "error": "deduction_date must be in YYYY-MM-DD format"}
                )
        
        # Validate cycle_id if provided
        if cycle_id is not None:
            cycle_id_str = str(cycle_id)
            if cycle_id_str not in payroll_cycles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                    }
                )
        
        # Validate status if provided
        valid_statuses = ["valid", "invalid_limit_exceeded"]
        if status is not None and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                }
            )
        
        timestamp = "2025-12-12T12:00:00"
        
        # Update only the fields that are provided
        if employee_id is not None:
            deduction["employee_id"] = str(employee_id)
        
        if deduction_rule_id is not None:
            deduction["deduction_rule_id"] = str(deduction_rule_id)
        
        if amount is not None:
            deduction["amount"] = str(amount_float)
        
        if deduction_date is not None:
            deduction["deduction_date"] = deduction_date_str
        
        if cycle_id is not None:
            deduction["cycle_id"] = str(cycle_id) if cycle_id else None
        
        if status is not None:
            deduction["status"] = status
        
        deduction["last_updated"] = timestamp
        
        return json.dumps(
            {
                "success": True,
                "message": f"Payroll deduction '{deduction_id_str}' has been updated successfully",
                "deduction": deduction,
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
                "name": "edit_payroll_deduction",
                "description": (
                    "Edit (update) an existing payroll deduction. "
                    "This tool is for UPDATING deductions only, not creating them. "
                    "deduction_id is REQUIRED to identify which deduction to update. "
                    "All other fields are optional - only provided fields will be updated. "
                    "Validates employee exists and has 'active' status if employee_id is provided. "
                    "Validates deduction rule exists and has 'active' status if deduction_rule_id is provided. "
                    "Validates payroll cycle exists if cycle_id is provided."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deduction_id": {
                            "type": "string",
                            "description": "ID of the deduction to update (REQUIRED)",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Optional: Update employee ID. Must be an active employee.",
                        },
                        "deduction_rule_id": {
                            "type": "string",
                            "description": "Optional: Update deduction rule ID. Must be an active rule.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "Optional: Update deduction amount (must be non-negative)",
                        },
                        "deduction_date": {
                            "type": "string",
                            "description": "Optional: Update date of the deduction in YYYY-MM-DD format",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional: Update ID of the payroll cycle",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional: Update status of the deduction. Valid values: 'valid', 'invalid_limit_exceeded'",
                            "enum": ["valid", "invalid_limit_exceeded"],
                        },
                    },
                    "required": ["deduction_id"],
                },
            },
        }

