import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateBenefitRecord(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        name: str,
        current_cost: float,
        previous_year_cost: float,
        enrollment_window: str = 'open',
        status: Optional[str] = "active",
        cost_variance_percent: Optional[float] = None
    ) -> str:
        """
        Create a new benefit plan record.
        """
        benefit_plans = data.get("benefit_plans", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required fields
        if not name:
            return json.dumps({
                "success": False,
                "error": "name is required"
            })
        
        if current_cost is None:
            return json.dumps({
                "success": False,
                "error": "current_cost is required"
            })
        
        if previous_year_cost is None:
            return json.dumps({
                "success": False,
                "error": "previous_year_cost is required"
            })
        
        # Validate name uniqueness
        for plan_id, plan in benefit_plans.items():
            if plan.get("name") == name:
                return json.dumps({
                    "success": False,
                    "error": f"Benefit plan with name '{name}' already exists (plan_id: '{plan_id}')"
                })
        
        # Validate status
        if status:
            valid_statuses = ["active", "inactive"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        else:
            status = "active"  # Default to active if not provided
        
        # Validate enrollment_window
        valid_enrollment_windows = ["open", "closed"]
        if enrollment_window not in valid_enrollment_windows:
            return json.dumps({
                "success": False,
                "error": f"Invalid enrollment_window. Must be one of: {', '.join(valid_enrollment_windows)}"
            })
        
        # Calculate cost_variance_percent if not provided
        if cost_variance_percent is None:
            if previous_year_cost != 0:
                cost_variance_percent = ((current_cost - previous_year_cost) / previous_year_cost) * 100
            else:
                cost_variance_percent = 0.0
        
        # Generate new plan_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_plan_id = generate_id(benefit_plans)
        
        # Create new benefit plan record
        new_benefit_plan = {
            "plan_id": new_plan_id,
            "name": name,
            "status": status,
            "current_cost": str(current_cost),
            "previous_year_cost": str(previous_year_cost),
            "enrollment_window": enrollment_window,
            "cost_variance_percent": f"{cost_variance_percent:.2f}",
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        benefit_plans[new_plan_id] = new_benefit_plan
        
        return json.dumps({
            "success": True,
            "benefit_plan": new_benefit_plan
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_benefit_record",
                "description": "Create a new benefit plan record. Validates name uniqueness and calculates cost_variance_percent if not provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the benefit plan (required, must be unique)"
                        },
                        "current_cost": {
                            "type": "number",
                            "description": "Current year cost (required)"
                        },
                        "previous_year_cost": {
                            "type": "number",
                            "description": "Previous year cost (required)"
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "Enrollment window status: open, closed (optional, default: 'open')",
                            "enum": ["open", "closed"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Plan status: active, inactive (optional, default: 'active')",
                            "enum": ["active", "inactive"]
                        },
                        "cost_variance_percent": {
                            "type": "number",
                            "description": "Cost variance percentage (optional, will be calculated if not provided)"
                        }
                    },
                    "required": ["name", "current_cost", "previous_year_cost"]
                }
            }
        }
