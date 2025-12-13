import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ApproveOrUpdateEarning(Tool):
    """
    Approve or update a payroll earning.
    - Updates the status of a payroll earning (pending, approved, rejected, require_justification).
    - Can update earning amount and earning type.
    - Validates the earning exists before updating.
    - Updates the last_updated timestamp.
    - Returns the updated earning details or an error.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        earning_id: str,
        status: Optional[str] = None,
        amount: Optional[float] = None,
        earning_type: Optional[str] = None,
        cycle_id: Optional[str] = None,
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

        payroll_earnings_dict = data.get("payroll_earnings", {})
        if not isinstance(payroll_earnings_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_earnings container: expected dict at data['payroll_earnings']",
                }
            )

        # Validate earning_id is provided
        if not earning_id:
            return json.dumps({"success": False, "error": "earning_id is required"})

        # Convert earning_id to string for consistent comparison
        earning_id_str = str(earning_id)

        # Check if the earning exists
        if earning_id_str not in payroll_earnings_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll earning with ID '{earning_id_str}' not found",
                }
            )

        # Get the existing earning
        earning = payroll_earnings_dict[earning_id_str]
        if not isinstance(earning, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid earning data for ID '{earning_id_str}'",
                }
            )

        # At least one field must be provided for update
        if not status and not amount and not earning_type:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field (status, amount, or earning_type) must be provided for update",
                }
            )

        # Validate status if provided
        valid_statuses = ["pending", "approved", "rejected", "require_justification"]
        if status and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
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
        if cycle_id:
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

        # Validate amount if provided
        if amount:
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

        # Update the earning with new values
        if status:
            earning["status"] = status
        
        if amount:
            earning["amount"] = amount
            
            # Re-evaluate status based on new amount if earning_type is bonus
            current_earning_type = earning_type if earning_type else earning.get("earning_type")
            if current_earning_type == "bonus" and amount > 5000:
                # If status wasn't explicitly set to approved/rejected, set to require_justification
                if status is None and earning.get("status") not in ["approved", "rejected"]:
                    earning["status"] = "require_justification"
        
        if earning_type:
            earning["earning_type"] = earning_type
            
            # Re-evaluate status based on new earning_type
            current_amount = amount if amount else earning.get("amount", 0)
            if earning_type == "bonus" and current_amount > 5000:
                # If status wasn't explicitly set to approved/rejected, set to require_justification
                if status is None and earning.get("status") not in ["approved", "rejected"]:
                    earning["status"] = "require_justification"

        # Update timestamp
        earning["last_updated"] = "2025-12-12T12:00:00"

        if cycle_id:
            earning["cycle_id"] = cycle_id

        return json.dumps(
            {
                "success": True,
                "payroll_earning": earning,
                "message": f"Payroll earning '{earning_id_str}' updated successfully",
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
                "name": "approve_or_update_earning",
                "description": (
                    "Approve or update an existing payroll earning. "
                    "Can update the status (pending, approved, rejected, require_justification), "
                    "amount, and/or earning type. "
                    "Automatically re-evaluates status if bonus amount exceeds $5,000 after update. "
                    "Updates the last_updated timestamp automatically. "
                    "Returns the updated earning details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "earning_id": {
                            "type": "string",
                            "description": "The ID of the payroll earning to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. New status for the earning. Valid values: 'pending', 'approved', 'rejected', 'require_justification'."
                        },
                        "amount": {
                            "type": "number",
                            "description": "Optional. New earning amount. Must be greater than 0.",
                        },
                        "earning_type": {
                            "type": "string",
                            "description": "Optional. New earning type. Valid values: 'bonus', 'incentive', 'allowance', 'payroll input', 'commission'."
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional. The ID of the payroll cycle.",
                        }
                    },
                    "required": ["earning_id"],
                },
            },
        }