import json
from typing import Any, Dict, Optional, Union
from tau_bench.envs.tool import Tool


class CreatePayrollEarning(Tool):
    """
    Create a new payroll earning record in the system.
    - Requires employee_id, cycle_id, earning_type, and amount.
    - Optionally accepts status and justification_notes.
    - Validates that employee and cycle exist.
    - Validates earning_type enum and amount is non-negative.
    - Auto-generates earning_id, created_at, and last_updated.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        earning_type: str,
        amount: Union[int, float],
        status: Optional[str] = None,
        justification_notes: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "earning": {...}} on success
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

        earnings_dict = data.get("payroll_earnings", {})
        if not isinstance(earnings_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid earnings container: expected dict at data['payroll_earnings']",
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

        cycles_dict = data.get("payroll_cycles", {})
        if not isinstance(cycles_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid cycles container: expected dict at data['payroll_cycles']",
                }
            )

        # Validate required fields
        if employee_id is None:
            return json.dumps({"success": False, "error": "employee_id is required"})

        if cycle_id is None:
            return json.dumps({"success": False, "error": "cycle_id is required"})

        if earning_type is None or not earning_type.strip():
            return json.dumps(
                {
                    "success": False,
                    "error": "earning_type is required and cannot be empty",
                }
            )

        if amount is None:
            return json.dumps({"success": False, "error": "amount is required"})

        # Convert IDs to strings for consistent comparison
        employee_id_str = str(employee_id)
        cycle_id_str = str(cycle_id)

        # Validate employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        # Validate cycle exists
        if cycle_id_str not in cycles_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                }
            )

        # Validate earning_type enum
        valid_earning_types = ["bonus", "incentive", "allowance", "overtime"]
        if earning_type not in valid_earning_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid earning_type: '{earning_type}'. Must be one of {valid_earning_types}",
                }
            )

        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float < 0:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid amount: must be non-negative (>= 0)",
                    }
                )
        except (TypeError, ValueError):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid amount: '{amount}' must be a number",
                }
            )

        # Validate status enum if provided
        valid_statuses = ["pending", "approved", "require_justification"]
        if status is not None:
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status: '{status}'. Must be one of {valid_statuses}",
                    }
                )
        else:
            # Default status
            status = "pending"

        # Generate new earning_id (find max existing ID and add 1)
        if earnings_dict:
            try:
                max_id = max(int(eid) for eid in earnings_dict.keys())
                new_earning_id = str(max_id + 1)
            except (ValueError, TypeError):
                # If IDs are not numeric, use length + 1
                new_earning_id = str(len(earnings_dict) + 1)
        else:
            new_earning_id = "1"

        # Generate timestamps (use static date for consistency)
        current_time = "2025-11-22T12:00:00"

        # Create new earning record
        new_earning = {
            "earning_id": new_earning_id,
            "employee_id": employee_id_str,
            "cycle_id": cycle_id_str,
            "earning_type": earning_type,
            "amount": amount_float,
            "status": status,
            "justification_notes": justification_notes if justification_notes else "",
            "created_at": current_time,
            "last_updated": current_time,
        }

        # Add to earnings dictionary
        earnings_dict[new_earning_id] = new_earning

        return json.dumps(
            {
                "success": True,
                "earning": new_earning,
                "message": f"Payroll earning {new_earning_id} created successfully",
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
                "name": "create_payroll_earning",
                "description": "Creates a new payroll earning record in the HR system. Payroll earnings represent additional compensation beyond base salary, such as bonuses, incentives, allowances, or overtime pay. This tool is used to record these additional earnings for employees within a specific payroll cycle. The earning must be linked to an existing employee and an active payroll cycle. The earning type must be one of the predefined categories, and the amount must be non-negative. Earnings are created with a 'pending' status by default and can be approved later through the approval workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The unique identifier of the employee receiving the earning. Must reference an existing employee in the system. ",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "The unique identifier of the payroll cycle to which this earning belongs. Must reference an existing payroll cycle in the system. ",
                        },
                        "earning_type": {
                            "type": "string",
                            "description": "The type of earning being recorded. Must be one of: 'bonus' (one-time performance or achievement bonuses), 'incentive' (sales incentives or performance incentives), 'allowance' (travel, housing, or other allowances), 'overtime' (overtime pay). This is a required field.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "The monetary amount of the earning in USD. Must be a non-negative number (>= 0). ",
                        },
                        "status": {
                            "type": "string",
                            "description": "The approval status of the earning. Must be one of: 'pending' (awaiting approval, default), 'approved' (approved for payment), 'require_justification' (needs additional justification before approval). If not provided, defaults to 'pending'.",
                        },
                        "justification_notes": {
                            "type": "string",
                            "description": "Optional notes providing justification or explanation for the earning. Useful for documenting the reason for bonuses, special allowances, or other additional compensation.",
                        },
                    },
                    "required": ["employee_id", "cycle_id", "earning_type", "amount"],
                },
            },
        }

