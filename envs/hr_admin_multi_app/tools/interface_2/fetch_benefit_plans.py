import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class FetchBenefitPlans(Tool):
    """
    Fetch benefit plans from the database with optional filtering.
    Used to discover existing plans and verify plan status before enrollment or updates.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        plan_id: Optional[str] = None,
        enrollment_window: Optional[str] = None,
        status: str = "active",
    ) -> str:
        """
        Fetch benefit plans with optional filters.
        
        Args:
            data: Dictionary containing benefit_plans
            plan_id: Optional specific plan ID to fetch
            enrollment_window: Optional filter by enrollment window ('open' or 'closed')
            status: Filter by status (default: 'active')
            
        Returns:
            JSON string with success status and list of matching benefit plans
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        benefit_plans = data.get("benefit_plans", {})
        if not isinstance(benefit_plans, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid benefit_plans container: expected dict at data['benefit_plans']",
                }
            )
        
        # If plan_id is provided, fetch specific plan
        if plan_id is not None:
            plan_id_str = str(plan_id)
            if plan_id_str not in benefit_plans:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Benefit plan with ID '{plan_id_str}' not found",
                    }
                )
            
            plan = benefit_plans[plan_id_str]
            return json.dumps(
                {
                    "success": True,
                    "count": 1,
                    "plans": [plan],
                }
            )
        
        # Filter plans based on criteria
        filtered_plans = []
        
        for plan in benefit_plans.values():
            # Filter by status
            if status and plan.get("status") != status:
                continue
            
            # Filter by enrollment_window if provided
            if enrollment_window is not None and plan.get("enrollment_window") != enrollment_window:
                continue
            
            filtered_plans.append(plan)
        
        # Return results
        if not filtered_plans:
            return json.dumps(
                {
                    "success": True,
                    "count": 0,
                    "plans": [],
                    "message": "No benefit plans found matching the specified criteria",
                }
            )
        
        return json.dumps(
            {
                "success": True,
                "count": len(filtered_plans),
                "plans": filtered_plans,
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
                "name": "fetch_benefit_plans",
                "description": (
                    "Fetch benefit plans from the database with optional filtering. "
                    "Used to discover existing plans, identify whether a benefit plan already exists, "
                    "and verify plan status (active/inactive) and enrollment window (open/closed) "
                    "before enrollment or updates. "
                    "Can fetch a specific plan by ID or filter plans by enrollment window and status. "
                    "Returns a list of matching benefit plans with details including plan_id, name, "
                    "status, current_cost, previous_year_cost, enrollment_window, cost_variance_percent, "
                    "created_at, and last_updated."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                            "description": "Optional: Specific benefit plan ID to fetch. If provided, returns only that plan.",
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "Optional: Filter by enrollment window status ('open' or 'closed')",
                            "enum": ["open", "closed"],
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by plan status (default: 'active'). Valid values: 'active', 'inactive'",
                            "enum": ["active", "inactive"],
                        },
                    },
                    "required": [],
                },
            },
        }

