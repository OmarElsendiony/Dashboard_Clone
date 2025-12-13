import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ObtainPendingEarnings(Tool):
    """
    Retrieve pending payroll earnings.
    - Returns all payroll earnings with 'pending' status.
    - Returns earning details including employee, type, amount, and status.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        earning_type: str = "pending",
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payroll_earnings": [...]} on success
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

        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})

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

        # Convert employee_id to string if provided
        employee_id_str = str(employee_id) if employee_id else None

        # Validate employee exists if employee_id is provided
        if employee_id_str and employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        # Validate earning_type if provided
        valid_earning_types = ["bonus", "incentive", "allowance", "payroll input", "commission"]
        if earning_type and earning_type not in valid_earning_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid earning_type '{earning_type}'. Must be one of: {', '.join(valid_earning_types)}",
                }
            )

        # Retrieve pending payroll earnings
        pending_earnings = []

        for earning_id, earning in payroll_earnings_dict.items():
            if not isinstance(earning, dict):
                continue

            # Filter by status - only 'pending'
            earning_status = earning.get("status")
            if earning_status != "pending":
                continue

            # Filter by employee_id if provided
            if employee_id_str:
                earning_employee_id = str(earning.get("employee_id", ""))
                if earning_employee_id != employee_id_str:
                    continue

            # Filter by earning_type if provided
            if earning_type:
                earning_earning_type = earning.get("earning_type")
                if earning_earning_type != earning_type:
                    continue

            # Add matching earning
            earning_copy = earning.copy()
            pending_earnings.append(earning_copy)

        # Sort by created_at (oldest first) for FIFO approval workflow
        pending_earnings.sort(
            key=lambda x: x.get("created_at", ""), 
            reverse=False
        )

        return json.dumps(
            {
                "success": True,
                "payroll_earnings": pending_earnings,
                "count": len(pending_earnings),
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
                "name": "obtain_pending_earnings",
                "description": (
                    "Retrieve payroll earnings with 'pending' status. "
                    "Returns all earnings filter by employee_id to get pending earnings for a specific employee. "
                    "Can optionally filter by earning_type (bonus, incentive, allowance, payroll input, commission). "
                    "Returns earning details including earning_id, employee_id, earning_type, amount, status, "
                    "created_at, and last_updated. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Filter pending earnings by specific employee ID.",
                        },
                        "earning_type": {
                            "type": "string",
                            "description": "The type of earning. Accepted values: 'bonus', 'incentive', 'allowance', 'payroll input', 'commission'.",
                        }
                    },
                    "required": ["employee_id"],
                },
            },
        }