import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateNewDeduction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
        deduction_rule_id: str,
        amount: float,
        deduction_date: str,
        status: str = 'valid'
    ) -> str:
        """
        Create a new deduction record.
        """
        deductions = data.get("deductions", {})
        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        deduction_rules = data.get("deduction_rules", {})
        timestamp = "2025-12-12T12:00:00"
        
        # Validate required fields
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        if not cycle_id:
            return json.dumps({
                "success": False,
                "error": "cycle_id is required"
            })
        
        if not deduction_rule_id:
            return json.dumps({
                "success": False,
                "error": "deduction_rule_id is required"
            })
        
        if amount is None:
            return json.dumps({
                "success": False,
                "error": "amount is required"
            })
        
        if not deduction_date:
            return json.dumps({
                "success": False,
                "error": "deduction_date is required"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        # Validate cycle exists
        if cycle_id not in payroll_cycles:
            return json.dumps({
                "success": False,
                "error": f"cycle_id '{cycle_id}' does not reference a valid payroll cycle"
            })
        
        # Validate deduction_rule exists
        if deduction_rule_id not in deduction_rules:
            return json.dumps({
                "success": False,
                "error": f"deduction_rule_id '{deduction_rule_id}' does not reference a valid deduction rule"
            })
        
        deduction_rule = deduction_rules[deduction_rule_id]
        
        # Validate deduction_rule is active
        if deduction_rule.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"Deduction rule '{deduction_rule_id}' is not active (status is '{deduction_rule.get('status')}')"
            })
        
        # Validate status
        valid_statuses = ["valid", "invalid_limit_exceeded"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Generate new deduction_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_deduction_id = generate_id(deductions)
        
        # Create new deduction record
        new_deduction = {
            "deduction_id": new_deduction_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "deduction_rule_id": deduction_rule_id,
            "amount": str(amount),
            "deduction_date": deduction_date,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        deductions[new_deduction_id] = new_deduction
        
        return json.dumps({
            "success": True,
            "deduction": new_deduction
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_deduction",
                "description": "Create a new deduction record. Validates employee, cycle, and deduction_rule exist, and deduction_rule is active.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Payroll cycle ID (required)"
                        },
                        "deduction_rule_id": {
                            "type": "string",
                            "description": "Deduction rule ID (required)"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Deduction amount (required)"
                        },
                        "deduction_date": {
                            "type": "string",
                            "description": "Deduction date in YYYY-MM-DD format (required)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Deduction status: valid, invalid_limit_exceeded (optional, default: 'valid')",
                            "enum": ["valid", "invalid_limit_exceeded"]
                        }
                    },
                    "required": ["employee_id", "cycle_id", "deduction_rule_id", "amount", "deduction_date"]
                }
            }
        }
