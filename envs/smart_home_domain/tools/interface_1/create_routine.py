import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRoutine(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        creator_id: str,
        routine_name: str,
        description: Optional[str] = None,
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # Implement your tool logic here
        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        routines = data.get("routines", {})
        homes = data.get("homes", {})

        # Find home_id if home_name is provided
        if home_name and not home_id:
            for h_id, home in homes.items():
                if home.get("home_name").strip().lower() == home_name.strip().lower():
                    home_id = h_id
                    break

        if not home_id:
            return json.dumps(
                {"success": False, "error": "Home ID or name must be provided"}
            )
        if not routine_name:
            return json.dumps(
                {"success": False, "error": "Routine name must be provided"}
            )
        if not creator_id:
            return json.dumps(
                {"success": False, "error": "Creator ID must be provided"}
            )
        # check if the rountine_name already exists in the home
        for routine in routines.values():
            if (
                routine.get("home_id") == home_id
                and routine.get("routine_name").strip().lower()
                == routine_name.strip().lower()
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Routine name '{routine_name}' already exists in the home.",
                    }
                )
        # check of the creator_id exists in users
        users = data.get("users", {})
        if creator_id not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Creator ID '{creator_id}', user does not exist.",
                }
            )
        # Check that the creator is a member of the home
        home_users = data.get("home_users", {})
        home_user = None
        for _, _user in home_users.items():
            if _user.get("user_id") == creator_id and _user.get("home_id") == home_id:
                home_user = _user
                break

        if not home_user:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{creator_id}' is not a member of the home.",
                }
            )

        # Create the new routine
        routine_id = generate_id(routines)
        timestamp = "2025-12-19T23:59:00"
        new_routine = {
            "routine_id": str(routine_id),
            "routine_name": routine_name,
            "home_id": str(home_id),
            "created_by_user_id": str(creator_id),
            "description": description or "",
            "status": "disabled",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routines[str(routine_id)] = new_routine
        return json.dumps({"success": True, "routine": new_routine})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_routine",
                "description": "Create a new routine in a specific home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home.",
                        },
                        "routine_name": {
                            "type": "string",
                            "description": "The name of the routine.",
                        },
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home.",
                        },
                        "creator_id": {
                            "type": "string",
                            "description": "The ID of the user creating the routine.",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the routine.",
                        },
                    },
                },
                "required": ["routine_name", "creator_id"],
            },
        }
