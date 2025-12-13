import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateDeductionData(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        deduction_id: str,
        amount: Optional[float] = None,
        deduction_date: Optional[str] = None,
        deduction_rule_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Update an existing deduction record.
        Only provided fields will be updated.
        """
        deductions = data.get("deductions", {})
        deduction_rules = data.get("deduction_rules", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required parameter
        if not deduction_id:
            return json.dumps({
                "success": False,
                "error": "deduction_id is required"
            })
        
        # Validate deduction exists
        if deduction_id not in deductions:
            return json.dumps({
                "success": False,
                "error": f"deduction_id '{deduction_id}' does not reference a valid deduction"
            })
        
        deduction = deductions[deduction_id]
        
        # Check if at least one field is being updated
        update_fields = [amount, deduction_date, deduction_rule_id, status]
        if all(field is None for field in update_fields):
            return json.dumps({
                "success": False,
                "error": "At least one field must be provided to update"
            })
        
        # Validate deduction_rule_id if provided
        if deduction_rule_id is not None:
            if deduction_rule_id not in deduction_rules:
                return json.dumps({
                    "success": False,
                    "error": f"deduction_rule_id '{deduction_rule_id}' does not reference a valid deduction rule"
                })
            
            deduction_rule = deduction_rules[deduction_rule_id]
            if deduction_rule.get("status") != "active":
                return json.dumps({
                    "success": False,
                    "error": f"Deduction rule '{deduction_rule_id}' is not active (status is '{deduction_rule.get('status')}')"
                })
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["valid", "invalid_limit_exceeded"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Update fields
        if amount is not None:
            deduction["amount"] = str(amount)
        if deduction_date is not None:
            deduction["deduction_date"] = deduction_date
        if deduction_rule_id is not None:
            deduction["deduction_rule_id"] = deduction_rule_id
        if status is not None:
            deduction["status"] = status
        
        # Update timestamp
        deduction["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "deduction": deduction
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_deduction_data",
                "description": "Update an existing deduction record. Only provided fields will be updated. Validates deduction_rule exists and is active if provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deduction_id": {
                            "type": "string",
                            "description": "Deduction ID to update (required)"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Deduction amount (optional)"
                        },
                        "deduction_date": {
                            "type": "string",
                            "description": "Deduction date in YYYY-MM-DD format (optional)"
                        },
                        "deduction_rule_id": {
                            "type": "string",
                            "description": "Deduction rule ID (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Deduction status: valid, invalid_limit_exceeded (optional)",
                            "enum": ["valid", "invalid_limit_exceeded"]
                        }
                    },
                    "required": ["deduction_id"]
                }
            }
        }
