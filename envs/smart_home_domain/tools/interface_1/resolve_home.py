import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ResolveHome(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_email: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Resolve and return home(s) associated to the user information user_email or user_id.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        users = data.get("users", {})
        homes = data.get("homes", {})

        if not user_email and not user_id:
            return json.dumps(
                {"success": False, "error": "Either user_email or user_id is required"}
            )
        user = {}
        # Search by user_email if provided
        if user_email:
            for u_id, u_data in users.items():
                if u_data.get("email") == user_email:
                    user = u_data
                    break
            if not user:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with email '{user_email}' not found",
                    }
                )
        # Search by user_id if provided
        elif user_id:
            user = users.get(user_id)
            if not user:
                return json.dumps(
                    {"success": False, "error": f"User with id '{user_id}' not found"}
                )
        user_homes = [
            home_data
            for _, home_data in homes.items()
            if home_data.get("owner_id") == user.get("user_id")
        ]
        user_homes_copy = [home.copy() for home in user_homes]
        _ = [home.pop("owner_id", None) or home for home in user_homes_copy]
        return json.dumps({"success": True, "user": user, "homes": user_homes_copy})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_home",
                "description": "Resolve and return home(s) associated to the user information user_email or user_id",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "Email of the user to retrieve associated home(s)",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "ID of the user to retrieve associated home(s)",
                        },
                    },
                    "required": [],
                },
            },
        }
