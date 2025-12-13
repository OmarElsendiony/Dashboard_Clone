import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class GetBenefitRecords(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        name: Optional[str] = None,
        enrollment_window: Optional[str] = None,
        status: str = 'active'
    ) -> str:
        """
        Get benefit plan record(s) based on filter criteria.
        Returns all benefit plans that match the specified filters.
        """
        benefit_plans = data.get("benefit_plans", {})
        results = []
        
        # Validate enrollment_window if provided
        if enrollment_window:
            valid_enrollment_windows = ["open", "closed"]
            if enrollment_window not in valid_enrollment_windows:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid enrollment_window. Must be one of: {', '.join(valid_enrollment_windows)}",
                    "count": 0,
                    "benefit_plans": []
                })
        
        # Validate status
        valid_statuses = ["active", "inactive"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                "count": 0,
                "benefit_plans": []
            })
        
        # Filter benefit plans
        for plan_id, plan in benefit_plans.items():
            match = True
            
            if name and plan.get("name") != name:
                match = False
            if enrollment_window and plan.get("enrollment_window") != enrollment_window:
                match = False
            if status and plan.get("status") != status:
                match = False
            
            if match:
                # Create a copy of the plan to avoid modifying the original
                plan_copy = plan.copy()
                results.append(plan_copy)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "benefit_plans": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_benefit_records",
                "description": "Get benefit plan record(s) based on filter criteria. Returns all benefit plans that match the specified filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Filter by benefit plan name (optional)"
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "Filter by enrollment window: open, closed (optional)",
                            "enum": ["open", "closed"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: active, inactive (optional, default: 'active')",
                            "enum": ["active", "inactive"]
                        }
                    },
                    "required": []
                }
            }
        }
