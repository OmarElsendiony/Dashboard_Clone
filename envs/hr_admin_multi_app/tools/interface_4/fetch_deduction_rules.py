import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class FetchDeductionRules(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        deduction_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Fetch deduction rule(s) based on filter criteria.
        Returns all deduction rules that match the specified filters.
        """
        deduction_rules = data.get("deduction_rules", {})
        results = []
        
        # Validate deduction_type if provided
        if deduction_type:
            valid_deduction_types = ["benefit_contribution", "repayment_of_overpayment", "loan", "retirement", "insurance", "tax", "garnishment"]
            if deduction_type not in valid_deduction_types:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid deduction_type. Must be one of: {', '.join(valid_deduction_types)}",
                    "count": 0,
                    "deduction_rules": []
                })
        
        # Validate status if provided
        if status:
            valid_statuses = ["active", "inactive"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    "count": 0,
                    "deduction_rules": []
                })
        
        # Filter deduction rules
        for rule_id, rule in deduction_rules.items():
            match = True
            
            if deduction_type and rule.get("deduction_type") != deduction_type:
                match = False
            if status and rule.get("status") != status:
                match = False
            
            if match:
                # Create a copy of the rule to avoid modifying the original
                rule_copy = rule.copy()
                results.append(rule_copy)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "deduction_rules": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_deduction_rules",
                "description": "Fetch deduction rule(s) based on filter criteria. Returns all deduction rules that match the specified filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deduction_type": {
                            "type": "string",
                            "description": "Filter by deduction type: benefit_contribution, repayment_of_overpayment, loan, retirement, insurance, tax, garnishment (optional)",
                            "enum": ["benefit_contribution", "repayment_of_overpayment", "loan", "retirement", "insurance", "tax", "garnishment"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: active, inactive (optional)",
                            "enum": ["active", "inactive"]
                        }
                    },
                    "required": []
                }
            }
        }
