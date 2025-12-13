import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AssignEarningToEmployee(Tool):
    """
    Assign an earning to an employee.
    - Creates a new payroll earning record for an employee.
    - Records earning type (bonus, incentive, allowance, etc.) and amount.
    - Sets initial status based on amount (requires_justification if bonus > $5,000).
    - Validates employee exists and amount is positive.
    - Returns the created earning details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        earning_type: str,
        amount: float,
        cycle_id: str,
        status: Optional[str] = "pending",
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payroll_earning": {...}} on success
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

        payroll_earnings_dict = data.get("payroll_earnings", {})
        if not isinstance(payroll_earnings_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_earnings container: expected dict at data['payroll_earnings']",
                }
            )

        # Validate required parameters
        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})

        if not earning_type:
            return json.dumps({"success": False, "error": "earning_type is required"})

        if amount is None:
            return json.dumps({"success": False, "error": "amount is required"})

        # Convert employee_id to string for consistent comparison
        employee_id_str = str(employee_id)

        # Check if employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
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
        
        if cycle_id not in payroll_cycles_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle with ID '{cycle_id}' not found",
                }
            )        

        # Validate earning_type
        valid_earning_types = [
            "bonus",
            "incentive",
            "allowance",
            "payroll input",
            "commission",
        ]
        if earning_type not in valid_earning_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid earning_type '{earning_type}'. Must be one of: {', '.join(valid_earning_types)}",
                }
            )

        # Validate earning_type
        valid_earning_status = [
            "pending",
            "approved",
            "rejected",
            "require_justification",
        ]
        if status not in valid_earning_status:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid earning_status '{status}'. Must be one of: {', '.join(valid_earning_status)}",
                }
            )

        # Validate amount
        try:
            amount = float(amount)

            if amount <= 0:
                return json.dumps(
                    {
                        "success": False,
                        "error": "amount must be greater than 0",
                    }
                )
        except (ValueError, TypeError) as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid amount value: {str(e)}",
                }
            )

        # Determine initial status based on earning type and amount
        # Per schema: bonus > $5,000 requires justification

        if earning_type == "bonus" and amount > 5000:
            status = "require_justification"

        # Generate new earning_id
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_earning_id = generate_id(payroll_earnings_dict)

        timestamp = "2025-11-16T23:59:00"

        # Create new payroll earning
        new_earning = {
            "earning_id": new_earning_id,
            "employee_id": employee_id_str,
            "earning_type": earning_type,
            "cycle_id": cycle_id,
            "amount": amount,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        # Add to data
        payroll_earnings_dict[new_earning_id] = new_earning

        return json.dumps(
            {
                "success": True,
                "payroll_earning": new_earning,
                "message": f"Payroll earning created successfully with ID: {new_earning_id}",
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
                "name": "assign_earning_to_employee",
                "description": (
                    "Assign a payroll earning to an employee in a payroll cycle. "
                    "Creates a new payroll earning record with specified type and amount. "
                    "Valid earning types: bonus, incentive, allowance, payroll input, commission. "
                    "Sets status to 'require_justification' if bonus amount exceeds $5,000, "
                    "otherwise sets status to 'pending'. "
                    "Returns the created earning details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee to assign the earning to.",
                        },
                        "earning_type": {
                            "type": "string",
                            "description": "The type of earning. Accepted values: 'bonus', 'incentive', 'allowance', 'payroll input', 'commission'.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "The earning amount. Must be greater than 0.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "The ID of the payroll cycle.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the earning. Accepted values: 'pending', 'approved', 'rejected', 'require_justification'. Defaults to 'pending'.",
                        },
                    },
                    "required": ["employee_id", "earning_type", "amount", "cycle_id"],
                },
            },
        }
