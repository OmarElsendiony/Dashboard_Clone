import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreatePayrollEarningRecord(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        amount: float,
        earning_type: str = 'bonus',
        status: str = 'pending'
    ) -> str:
        """
        Create a new payroll earning record.
        """
        payroll_earnings = data.get("payroll_earnings", {})
        employees = data.get("employees", {})
        timestamp = "2025-12-12T12:00:00"
        
        # Validate required fields
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        if amount is None:
            return json.dumps({
                "success": False,
                "error": "amount is required"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        employee = employees[employee_id]
        
        # Validate employee is active
        if employee.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"Employee '{employee_id}' is not active (status is '{employee.get('status')}')"
            })
        
        # Validate earning_type
        valid_earning_types = ["bonus", "incentive", "allowance", "payroll input", "commission"]
        if earning_type not in valid_earning_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid earning_type. Must be one of: {', '.join(valid_earning_types)}"
            })
        
        # Validate status
        valid_statuses = ["pending", "approved", "rejected", "require_justification"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Generate new earning_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_earning_id = generate_id(payroll_earnings)
        
        # Create new payroll earning record
        new_earning = {
            "earning_id": new_earning_id,
            "employee_id": employee_id,
            "earning_type": earning_type,
            "amount": str(amount),
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        payroll_earnings[new_earning_id] = new_earning
        
        return json.dumps({
            "success": True,
            "payroll_earning": new_earning
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_payroll_earning_record",
                "description": "Create a new payroll earning record. Validates employee exists and is active, and earning_type is valid.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Earning amount (required)"
                        },
                        "earning_type": {
                            "type": "string",
                            "description": "Type of earning: bonus, incentive, allowance, payroll input, commission (optional, default: 'bonus')",
                            "enum": ["bonus", "incentive", "allowance", "payroll input", "commission"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Earning status: pending, approved, rejected, require_justification (optional, default: 'pending')",
                            "enum": ["pending", "approved", "rejected", "require_justification"]
                        }
                    },
                    "required": ["employee_id", "amount"]
                }
            }
        }
