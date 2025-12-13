import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ManagePayrollEarning(Tool):
    """
    Manage payroll earnings - create new or update/approve/reject existing earnings.
    Used to add earnings and approve or deny payroll earnings.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        earning_id: Optional[str] = None,
        earning_type: Optional[str] = None,
        amount: Optional[float] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Manage payroll earning - create new or update existing.
        
        Args:
            data: Dictionary containing payroll_earnings and employees
            employee_id: ID of the employee (required)
            earning_id: Optional earning ID to update existing earning
            earning_type: Type of earning (bonus, incentive, allowance, payroll input, commission)
            amount: Amount of the earning
            status: Status to set (pending, approved, rejected, require_justification)
            
        Returns:
            JSON string with success status and earning details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        payroll_earnings = data.get("payroll_earnings", {})
        if not isinstance(payroll_earnings, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_earnings container: expected dict at data['payroll_earnings']",
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
        
        # Validate required fields
        if not employee_id:
            return json.dumps(
                {"success": False, "error": "employee_id is required"}
            )
        
        employee_id_str = str(employee_id)
        
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
        
        # Valid earning types
        valid_earning_types = ["bonus", "incentive", "allowance", "payroll input", "commission"]
        
        # Valid statuses
        valid_statuses = ["pending", "approved", "rejected", "require_justification"]
        
        timestamp = "2025-11-16T23:59:00"
        
        # UPDATE MODE: If earning_id is provided (for approval/denial)
        if earning_id:
            earning_id_str = str(earning_id)
            
            if earning_id_str not in payroll_earnings:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payroll earning with ID '{earning_id_str}' not found",
                    }
                )
            
            earning = payroll_earnings[earning_id_str]
            
            # For approval operations, validate earning type
            if status in ["approved", "rejected"]:
                current_earning_type = earning.get("earning_type")
                
                # Check if earning type can be approved/rejected
                approvable_types = ["bonus", "incentive", "allowance", "payroll input"]
                if current_earning_type not in approvable_types:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot approve or reject earning type '{current_earning_type}'. Only bonus, incentive, allowance, and payroll input can be approved or rejected.",
                        }
                    )
            
            # Update fields if provided
            if earning_type:
                if earning_type not in valid_earning_types:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid earning_type value: '{earning_type}'. Must be one of {valid_earning_types}",
                        }
                    )
                earning["earning_type"] = earning_type
            
            if amount is not None:
                try:
                    amount_float = float(amount)
                    if amount_float < 0:
                        return json.dumps(
                            {"success": False, "error": "amount must be non-negative (≥ 0.00)"}
                        )
                    earning["amount"] = str(amount_float)
                    
                    # Check if bonus > 5000 requires justification
                    if earning.get("earning_type") == "bonus" and amount_float > 5000:
                        earning["status"] = "require_justification"
                    
                except (ValueError, TypeError):
                    return json.dumps(
                        {"success": False, "error": "amount must be a valid number"}
                    )
            
            if status:
                if status not in valid_statuses:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                        }
                    )
                earning["status"] = status
            
            earning["last_updated"] = timestamp
            
            action_message = "updated"
            if status == "approved":
                action_message = "approved"
            elif status == "rejected":
                action_message = "rejected"
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Payroll earning '{earning_id_str}' has been {action_message} successfully",
                    "earning": earning,
                    "action": action_message,
                }
            )
        
        # CREATE MODE: If earning_id is not provided
        else:
            # Validate required fields for creation
            if not earning_type:
                return json.dumps(
                    {"success": False, "error": "earning_type is required for creating a new earning"}
                )
            
            if amount is None:
                return json.dumps(
                    {"success": False, "error": "amount is required for creating a new earning"}
                )
            
            # Validate earning_type
            if earning_type not in valid_earning_types:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid earning_type value: '{earning_type}'. Must be one of {valid_earning_types}",
                    }
                )
            
            # Validate amount
            try:
                amount_float = float(amount)
                if amount_float < 0:
                    return json.dumps(
                        {"success": False, "error": "amount must be non-negative (≥ 0.00)"}
                    )
            except (ValueError, TypeError):
                return json.dumps(
                    {"success": False, "error": "amount must be a valid number"}
                )
            
            # Generate new earning ID
            def generate_earning_id(earnings: Dict[str, Any]) -> str:
                if not earnings:
                    return "1"
                try:
                    max_id = max(int(k) for k in earnings.keys() if k.isdigit())
                    return str(max_id + 1)
                except ValueError:
                    return "1"
            
            new_earning_id = generate_earning_id(payroll_earnings)
            
            # Determine status based on amount and type
            if earning_type == "bonus" and amount_float > 5000:
                default_status = "require_justification"
            else:
                default_status = "pending"
            
            # Create new earning
            new_earning = {
                "earning_id": new_earning_id,
                "employee_id": employee_id_str,
                "earning_type": earning_type,
                "amount": str(amount_float),
                "status": status if status else default_status,
                "created_at": timestamp,
                "last_updated": timestamp,
            }
            
            payroll_earnings[new_earning_id] = new_earning
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Payroll earning has been created successfully for employee '{employee.get('full_name')}' ({employee_id_str})",
                    "earning": new_earning,
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
                "name": "manage_payroll_earning",
                "description": (
                    "Manage payroll earnings - create new or update/approve/reject existing earnings. "
                    "CREATE MODE: If earning_id is not provided, creates a new payroll earning. "
                    "Requires employee_id, earning_type, and amount. "
                    "Validates employee exists and has 'active' status. "
                    "Validates earning_type is in the predefined list (bonus, incentive, allowance, payroll input, commission). "
                    "Validates amount ≥ 0.00. "
                    "Automatically sets status to 'require_justification' if earning_type is 'bonus' and amount > $5,000. "
                    "UPDATE MODE: If earning_id is provided, updates or approves/rejects the earning. "
                    "For approval/rejection, validates earning type is one of: bonus, incentive, allowance, payroll input. "
                    "Cannot approve/reject other earning types."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (required)",
                        },
                        "earning_id": {
                            "type": "string",
                            "description": "Optional: Earning ID to update/approve/reject an existing earning. If provided, enters UPDATE mode.",
                        },
                        "earning_type": {
                            "type": "string",
                            "description": "Type of earning (required for creation). Valid values: 'bonus', 'incentive', 'allowance', 'payroll input', 'commission'",
                            "enum": ["bonus", "incentive", "allowance", "payroll input", "commission"],
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount of the earning (required for creation, must be ≥ 0.00)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the earning (optional). Valid values: 'pending', 'approved', 'rejected', 'require_justification'. Defaults to 'pending' or 'require_justification' based on amount.",
                            "enum": ["pending", "approved", "rejected", "require_justification"],
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }

