import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ProcessBenefitPlan(Tool):
    """
    Process (create, update, or delete) a benefit plan in the system.
    Used to create new plans, update existing plans, activate/deactivate plans, or permanently delete plans.
    Supports updating by plan_id or by name. Use action parameter to control behavior or let it auto-detect.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        name: str,
        enrollment_window: str = "open",
        status: Optional[str] = "active",
        current_cost: Optional[float] = None,
        previous_year_cost: Optional[float] = None,
        action: Optional[str] = None,
        plan_id: Optional[str] = None,
    ) -> str:
        """
        Process a benefit plan - create new, update existing, or delete a plan.
        
        Args:
            data: Dictionary containing benefit_plans
            name: Name of the benefit plan (must be unique for new plans)
            enrollment_window: Enrollment window status ('open' or 'closed', default: 'open')
            status: Plan status ('active' or 'inactive', default: 'active'). Use 'inactive' to deactivate a plan.
            current_cost: Current year cost of the plan (required for create, optional for update, ignored for delete)
            previous_year_cost: Previous year cost of the plan (required for create, optional for update, ignored for delete)
            action: Optional action type ('create', 'update', 'delete'). If 'delete', removes the plan permanently.
                   If not provided, auto-detects: creates if plan doesn't exist, updates if it does.
            plan_id: Plan ID (optional for create, required for update/delete). For create, if not provided, a new ID will be generated.
            
        Returns:
            JSON string with success status and plan details
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
        
        # Helper function to generate a new plan ID
        def generate_plan_id(plans: Dict[str, Any]) -> str:
            """Generate a new plan ID by finding the maximum existing ID and incrementing."""
            if not plans:
                return "1"
            try:
                # Extract numeric IDs and find the max
                numeric_ids = []
                for key in plans.keys():
                    try:
                        numeric_ids.append(int(key))
                    except ValueError:
                        continue
                if numeric_ids:
                    return str(max(numeric_ids) + 1)
                return "1"
            except Exception:
                return "1"
        
        # Validate plan_id based on action
        if plan_id:
            plan_id = str(plan_id).strip()
            if not plan_id:
                plan_id = None
        
        # Validate action parameter
        valid_actions = ["create", "update", "delete"]
        if action and action not in valid_actions:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action value: '{action}'. Must be one of {valid_actions}",
                }
            )
        
        # Handle delete action
        if action == "delete":
            if not plan_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "plan_id is required for delete action",
                    }
                )
            if plan_id not in benefit_plans:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Plan with ID '{plan_id}' not found",
                    }
                )
            deleted_plan = benefit_plans.pop(plan_id)
            return json.dumps(
                {
                    "success": True,
                    "message": f"Benefit plan '{deleted_plan.get('name', plan_id)}' (ID: {plan_id}) has been deleted successfully",
                    "plan_id": plan_id,
                    "action": "deleted",
                }
            )
        
        # Validate required fields
        if not name or not name.strip():
            return json.dumps(
                {"success": False, "error": "name is required and cannot be empty"}
            )
        
        name_stripped = name.strip()
        
        # Determine action if not explicitly provided
        if action is None:
            # If plan_id is provided, check if it exists to determine action
            if plan_id:
                action = "update" if plan_id in benefit_plans else "create"
            else:
                # No plan_id provided, must be create
                action = "create"
        
        # Handle plan_id based on action
        if action == "create":
            # Generate plan_id if not provided
            if not plan_id:
                plan_id = generate_plan_id(benefit_plans)
            else:
                # Check if plan already exists with this ID
                if plan_id in benefit_plans:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Plan with ID '{plan_id}' already exists. Use action='update' to update it.",
                        }
                    )
            # Costs are required for create
            if current_cost is None:
                return json.dumps(
                    {"success": False, "error": "current_cost is required for create action"}
                )
            if previous_year_cost is None:
                return json.dumps(
                    {"success": False, "error": "previous_year_cost is required for create action"}
                )
        elif action == "update":
            # plan_id is required for update
            if not plan_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "plan_id is required for update action",
                    }
                )
            # Check if plan exists
            if plan_id not in benefit_plans:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Plan with ID '{plan_id}' not found. Use action='create' to create a new plan.",
                    }
                )
        
        # Check if plan exists (for later use)
        existing_plan_id = plan_id if plan_id in benefit_plans else None
        
        # Validate numeric fields if provided
        current_cost_float = None
        previous_year_cost_float = None
        
        if current_cost is not None:
            try:
                current_cost_float = float(current_cost)
                if current_cost_float < 0:
                    return json.dumps(
                        {"success": False, "error": "current_cost must be a positive number"}
                    )
            except (ValueError, TypeError):
                return json.dumps(
                    {"success": False, "error": "current_cost must be a valid number"}
                )
        
        if previous_year_cost is not None:
            try:
                previous_year_cost_float = float(previous_year_cost)
                if previous_year_cost_float < 0:
                    return json.dumps(
                        {"success": False, "error": "previous_year_cost must be a positive number"}
                    )
            except (ValueError, TypeError):
                return json.dumps(
                    {"success": False, "error": "previous_year_cost must be a valid number"}
                )
        
        # Validate enrollment_window
        valid_enrollment_windows = ["open", "closed"]
        if enrollment_window not in valid_enrollment_windows:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid enrollment_window value: '{enrollment_window}'. Must be one of {valid_enrollment_windows}",
                }
            )
        
        # Validate status
        valid_statuses = ["active", "inactive"]
        if status and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                }
            )
        
        # Set default status if None
        if status is None:
            status = "active"
        
        timestamp = "2025-12-12T12:00:00"
        
        if existing_plan_id:
            # Update existing plan
            existing_plan = benefit_plans[existing_plan_id]
            
            # Use provided costs or keep existing values
            if current_cost_float is None:
                current_cost_float = float(existing_plan.get("current_cost", 0))
            if previous_year_cost_float is None:
                previous_year_cost_float = float(existing_plan.get("previous_year_cost", 0))
            
            # Update name if provided and different
            if name_stripped and existing_plan.get("name") != name_stripped:
                existing_plan["name"] = name_stripped
            
            # Calculate cost variance percent
            if previous_year_cost_float == 0:
                cost_variance_percent = 0.0
            else:
                cost_variance_percent = ((current_cost_float - previous_year_cost_float) / previous_year_cost_float) * 100
            cost_variance_percent = round(cost_variance_percent, 2)
            
            existing_plan["status"] = status
            existing_plan["current_cost"] = str(current_cost_float)
            existing_plan["previous_year_cost"] = str(previous_year_cost_float)
            existing_plan["enrollment_window"] = enrollment_window
            existing_plan["cost_variance_percent"] = str(cost_variance_percent)
            existing_plan["last_updated"] = timestamp
            
            plan_name = existing_plan.get("name", name_stripped)
            return json.dumps(
                {
                    "success": True,
                    "message": f"Benefit plan '{plan_name}' (ID: {existing_plan_id}) has been updated successfully",
                    "plan": existing_plan,
                    "action": "updated",
                }
            )
        else:
            # Create new plan - check if plan_id already exists
            if plan_id in benefit_plans:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Plan with ID '{plan_id}' already exists. Use action='update' to update it.",
                    }
                )
            
            # Calculate cost variance percent
            if previous_year_cost_float == 0:
                cost_variance_percent = 0.0
            else:
                cost_variance_percent = ((current_cost_float - previous_year_cost_float) / previous_year_cost_float) * 100
            cost_variance_percent = round(cost_variance_percent, 2)
            
            new_plan = {
                "plan_id": plan_id,
                "name": name_stripped,
                "status": status,
                "current_cost": str(current_cost_float),
                "previous_year_cost": str(previous_year_cost_float),
                "enrollment_window": enrollment_window,
                "cost_variance_percent": str(cost_variance_percent),
                "created_at": timestamp,
                "last_updated": timestamp,
            }
            
            benefit_plans[plan_id] = new_plan
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Benefit plan '{name_stripped}' (ID: {plan_id}) has been created successfully",
                    "plan": new_plan,
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
                "name": "process_benefit_plan",
                "description": (
                    "Process (create, update, or delete) a benefit plan in the system. "
                    "Used to create new plans, update existing plans, activate/deactivate plans, or permanently delete plans. "
                    "plan_id is optional for create (will be auto-generated if not provided), required for update/delete actions. "
                    "Use action='create' to only create (fails if exists), action='update' to only update (fails if not exists), "
                    "action='delete' to permanently remove a plan, or omit action for auto-detect (creates if new, updates if exists). "
                    "current_cost and previous_year_cost are required for create, optional for update (uses existing values if not provided), ignored for delete. "
                    "To deactivate a plan temporarily, set status='inactive'. To remove permanently, use action='delete'. "
                    "Automatically calculates cost_variance_percent based on current and previous year costs. "
                    "Returns the created, updated, or deletion confirmation with plan details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": ["string", "null"],
                            "description": "Plan ID (optional for create - will be auto-generated if not provided, required for update/delete). For update/delete, provide existing plan_id.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the benefit plan (required, must be unique for new plans)",
                        },
                        "current_cost": {
                            "type": ["number", "null"],
                            "description": "Current year cost of the plan (required for create, optional for update, ignored for delete, must be >= 0)",
                        },
                        "previous_year_cost": {
                            "type": ["number", "null"],
                            "description": "Previous year cost of the plan (required for create, optional for update, ignored for delete, must be >= 0)",
                        },
                        "enrollment_window": {
                            "type": "string",
                            "description": "Enrollment window status (default: 'open'). Valid values: 'open', 'closed'",
                            "enum": ["open", "closed"],
                        },
                        "status": {
                            "type": "string",
                            "description": "Plan status (default: 'active'). Valid values: 'active', 'inactive'. Use 'active' to activate a plan, 'inactive' to temporarily deactivate it. Note: To permanently delete a plan, use action='delete' instead.",
                            "enum": ["active", "inactive"],
                        },
                        "action": {
                            "type": ["string", "null"],
                            "description": "Optional action type. Valid values: 'create' (only create, fails if exists), 'update' (only update, fails if not exists), 'delete' (permanently remove plan). If not provided, auto-detects: creates if plan doesn't exist, updates if it does.",
                            "enum": ["create", "update", "delete"],
                        },
                    },
                    "required": ["name"],
                },
            },
        }

