import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateBenefitRecord(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        plan_id: str,
        current_cost: Optional[float] = None,
        enrollment_window: Optional[str] = None,
        name: Optional[str] = None,
        previous_year_cost: Optional[float] = None,
        status: Optional[str] = "active",
        cost_variance_percent: Optional[float] = None
    ) -> str:
        """
        Update an existing benefit plan record.
        Only provided fields will be updated.
        """
        benefit_plans = data.get("benefit_plans", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required parameter
        if not plan_id:
            return json.dumps({
                "success": False,
                "error": "plan_id is required"
            })
        
        # Validate plan exists
        if plan_id not in benefit_plans:
            return json.dumps({
                "success": False,
                "error": f"plan_id '{plan_id}' does not reference a valid benefit plan"
            })
        
        plan = benefit_plans[plan_id]
        
        # Check if at least one field is being updated
        update_fields = [current_cost, enrollment_window, name, previous_year_cost, status, cost_variance_percent]
        if all(field is None for field in update_fields):
            return json.dumps({
                "success": False,
                "error": "At least one field must be provided to update"
            })
        
        # Validate name uniqueness if name is being updated
        if name is not None:
            if name != plan.get("name"):
                for pid, p in benefit_plans.items():
                    if pid != plan_id and p.get("name") == name:
                        return json.dumps({
                            "success": False,
                            "error": f"Benefit plan with name '{name}' already exists (plan_id: '{pid}')"
                        })
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["active", "inactive"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Validate enrollment_window if provided
        if enrollment_window is not None:
            valid_enrollment_windows = ["open", "closed"]
            if enrollment_window not in valid_enrollment_windows:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid enrollment_window. Must be one of: {', '.join(valid_enrollment_windows)}"
                })
        
        # Update fields
        if name is not None:
            plan["name"] = name
        if current_cost is not None:
            plan["current_cost"] = str(current_cost)
        if previous_year_cost is not None:
            plan["previous_year_cost"] = str(previous_year_cost)
        if enrollment_window is not None:
            plan["enrollment_window"] = enrollment_window
        if status is not None:
            plan["status"] = status
        
        # Calculate cost_variance_percent if cost fields are updated
        if current_cost is not None or previous_year_cost is not None:
            # Get current values (use updated values if provided, otherwise existing)
            curr_cost = current_cost if current_cost is not None else float(plan.get("current_cost", 0))
            prev_cost = previous_year_cost if previous_year_cost is not None else float(plan.get("previous_year_cost", 0))
            
            if prev_cost != 0:
                calculated_variance = ((curr_cost - prev_cost) / prev_cost) * 100
                plan["cost_variance_percent"] = f"{calculated_variance:.2f}"
            else:
                plan["cost_variance_percent"] = "0.00"
        elif cost_variance_percent is not None:
            plan["cost_variance_percent"] = f"{cost_variance_percent:.2f}"
        
        # Update timestamp
        plan["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "benefit_plan": plan
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_benefit_record",
                "description": "Update an existing benefit plan record. Only provided fields will be updated. Automatically recalculates cost_variance_percent if cost fields are updated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                            "description": "Plan ID to update (required)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the benefit plan (optional, must be unique)"
                        },
                        "current_cost": {
                            "type": "number",
                            "description": "Current year cost (optional)"
                        },
                        "previous_year_cost": {
                            "type": "number",
                            "description": "Previous year cost (optional)"
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "Enrollment window status: open, closed (optional)",
                            "enum": ["open", "closed"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Plan status: active, inactive (optional, default: 'active')",
                            "enum": ["active", "inactive"]
                        },
                        "cost_variance_percent": {
                            "type": "number",
                            "description": "Cost variance percentage (optional, will be recalculated if cost fields are updated)"
                        }
                    },
                    "required": ["plan_id"]
                }
            }
        }
