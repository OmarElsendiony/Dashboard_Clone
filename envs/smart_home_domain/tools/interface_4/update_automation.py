import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateAutomation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        automation_id: str,
        automation_name: Optional[str] = None,
        status: Optional[str] = None,
        description: Optional[str] = None,
        created_by_user_id: Optional[str] = None,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        routines_dict = data.get("routines", {})
        if not isinstance(routines_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routines container: expected dict at data['routines']",
                }
            )

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid homes container: expected dict at data['homes']",
                }
            )

        users_dict = data.get("users", {})
        if not isinstance(users_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid users container: expected dict at data['users']",
                }
            )

        # Validate required parameters
        if not automation_id:
            return json.dumps({"success": False, "error": "automation_id is required"})

        # Check that at least one update parameter is provided
        if (
            not automation_name
            and not status
            and not description
            and not created_by_user_id
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one of automation_name, status, description, or created_by_user_id must be provided for update",
                }
            )

        # Convert to strings for consistent comparison
        automation_id_str = str(automation_id).strip()
        routine_name_str = str(automation_name).strip() if automation_name else None
        status_str = str(status).strip() if status else None
        description_str = str(description).strip() if description else None
        created_by_user_id_str = (
            str(created_by_user_id).strip() if created_by_user_id else None
        )

        # Validate status if provided
        if status_str:
            valid_statuses = ["enabled", "disabled"]
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )

        # Check if automation exists
        if automation_id_str not in routines_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Automation with ID '{automation_id_str}' not found",
                }
            )

        automation = routines_dict[automation_id_str]
        if not isinstance(automation, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid automation data for ID '{automation_id_str}'",
                }
            )

        # Get household_id from the automation
        household_id_str = str(automation.get("home_id"))

        # Validate household exists
        if household_id_str not in homes_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Household with ID '{household_id_str}' not found",
                }
            )

        home_info = homes_dict[household_id_str]
        if not isinstance(home_info, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid household data for ID '{household_id_str}'",
                }
            )

        # Validate user exists if provided
        if created_by_user_id_str:
            if created_by_user_id_str not in users_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID '{created_by_user_id_str}' not found",
                    }
                )

        # Track updates made
        updates_made = []

        # Check if new routine_name conflicts with existing automations (excluding current automation)
        if routine_name_str:
            for rid, routine in routines_dict.items():
                if not isinstance(routine, dict):
                    continue

                # Skip the current automation being updated
                if str(rid) == automation_id_str:
                    continue

                if (
                    str(routine.get("home_id")) == household_id_str
                    and str(routine.get("routine_name", "")).strip() == routine_name_str
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Automation with name '{routine_name_str}' already exists in household '{household_id_str}' (routine_id: {rid})",
                        }
                    )

            # Update routine name
            old_routine_name = automation.get("routine_name")
            automation["routine_name"] = routine_name_str
            updates_made.append(
                f"routine_name from '{old_routine_name}' to '{routine_name_str}'"
            )

        # Update status if provided
        if status_str:
            old_status = automation.get("status")
            automation["status"] = status_str
            updates_made.append(f"status from '{old_status}' to '{status_str}'")

        # Update description if provided
        if description_str:
            automation["description"] = description_str
            updates_made.append(f"description to '{description_str}'")

        # Update created_by_user_id if provided
        if created_by_user_id_str:
            old_user_id = automation.get("created_by_user_id")
            automation["created_by_user_id"] = created_by_user_id_str
            updates_made.append(
                f"created_by_user_id from '{old_user_id}' to '{created_by_user_id_str}'"
            )

        # Update timestamp
        automation["updated_at"] = timestamp

        automation_return = automation.copy()
        automation_return["automation_id"] = automation_return.pop("routine_id")
        automation_return["automation_name"] = automation_return.pop("routine_name")
        automation_return["household_id"] = automation_return.pop("home_id")

        return json.dumps(
            {
                "success": True,
                "automation": automation_return,
                "message": f"Automation '{automation.get('routine_name')}' updated successfully.",
                "household_name": home_info.get("home_name"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_automation",
                "description": (
                    "Update automation information including name, status, description, and created_by_user_id. "
                    "Validates that the automation exists. "
                    "If automation_name is provided, ensures it's unique within the household (excluding the current automation). "
                    "If status is provided, validates it's either 'enabled' or 'disabled'. "
                    "If created_by_user_id is provided, validates that the user exists. "
                    "At least one of automation_name, status, description, or created_by_user_id must be provided for update. "
                    "Returns the updated automation details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "automation_id": {
                            "type": "string",
                            "description": "The ID of the automation to update.",
                        },
                        "automation_name": {
                            "type": "string",
                            "description": "Optional. The new name for the automation. Must be unique within the household.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. The new status of the automation. Accepted values: 'enabled', 'disabled'.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. The new description for the automation.",
                        },
                        "created_by_user_id": {
                            "type": "string",
                            "description": "Optional. The new user ID to assign as creator of the automation.",
                        },
                    },
                    "required": ["automation_id"],
                },
            },
        }
