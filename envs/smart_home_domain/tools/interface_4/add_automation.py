import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddAutomation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        name: str,
        household_id: str,
        created_by_user_id: str,
        status: str = "disabled",
        description: str = None,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

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
        if not name:
            return json.dumps({"success": False, "error": "name is required"})

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        if not created_by_user_id:
            return json.dumps(
                {"success": False, "error": "created_by_user_id is required"}
            )

        # Convert to strings for consistent comparison
        name_str = str(name).strip()
        household_id_str = str(household_id).strip()
        status_str = str(status).strip() if status else "disabled"
        description_str = str(description).strip() if description else ""
        created_by_user_id_str = str(created_by_user_id).strip()

        # Validate status
        valid_statuses = ["enabled", "disabled"]
        if status_str not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

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

        if created_by_user_id_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{created_by_user_id_str}' not found",
                }
            )

        # Check if routine_name already exists in this household (per schema unique constraint)
        for rid, routine in routines_dict.items():
            if not isinstance(routine, dict):
                continue

            if (
                str(routine.get("home_id")) == household_id_str
                and str(routine.get("routine_name", "")).strip() == name_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Automation with name '{name_str}' already exists in household '{household_id_str}' (routine_id: {rid})",
                    }
                )

        # Generate new routine_id
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_routine_id = generate_id(routines_dict)

        # Create new routine entry
        new_routine = {
            "routine_id": new_routine_id,
            "home_id": household_id_str,
            "created_by_user_id": created_by_user_id_str,
            "routine_name": name_str,
            "status": status_str,
            "description": description_str,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add to data
        routines_dict[new_routine_id] = new_routine

        new_routine_return = new_routine.copy()
        new_routine_return["automation_id"] = new_routine_return.pop("routine_id")
        new_routine_return["household_id"] = new_routine_return.pop("home_id")
        new_routine_return["automation_name"] = new_routine_return.pop("routine_name")

        return json.dumps(
            {
                "success": True,
                "automation": new_routine_return,
                "message": f"Automation '{name_str}' successfully created in household '{home_info.get('home_name')}' with ID: {new_routine_id}",
                "household_name": home_info.get("home_name"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_automation",
                "description": (
                    "Create a new automation in a household. "
                    "Validates that the household exists. "
                    "Validates that the user exists. "
                    "Ensures automation name is unique within the household. "
                    "Status defaults to 'disabled' and must be 'enabled' or 'disabled'. "
                    "Returns the created automation details including the generated automation_id. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the automation. Must be unique within the household.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household to create the automation in.",
                        },
                        "created_by_user_id": {
                            "type": "string",
                            "description": "The ID of the user creating the automation.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. The status of the automation. Accepted values: 'enabled', 'disabled'. Default: 'disabled'.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. Description of the automation.",
                        },
                    },
                    "required": ["name", "household_id", "created_by_user_id"],
                },
            },
        }
