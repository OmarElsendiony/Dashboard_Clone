import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class RemoveUserFromHome(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        user_id: str,
    ) -> str:
        """
        Remove a user's access to a home.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        home_users = data.get("home_users")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(home_users, dict):
            return json.dumps({"success": False, "error": "home_users store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        home = None
        for hid, h in homes.items():
            if h.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                home = h
                break
        
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        if not isinstance(user_id, str) or not user_id.strip():
            return json.dumps({"success": False, "error": "user_id must be provided"})
        user_id = user_id.strip()

        if home.get("owner_id") == user_id:
            return json.dumps({"success": False, "error": "Cannot remove the home owner"})

        found_id = None
        found_role = None
        for home_user_id, home_user in home_users.items():
            if home_user.get("home_id") == home_id and home_user.get("user_id") == user_id:
                found_id = home_user_id
                found_role = home_user.get("role")
                break

        if not found_id:
            return json.dumps({"success": False, "error": f"User '{user_id}' is not a member of home '{home_name}'"})
        
        # Per SOP: Cannot remove admin users
        if found_role == "admin":
            return json.dumps({"success": False, "error": "Cannot remove admin users from the home"})

        removed_record = home_users.pop(found_id)

        return json.dumps({"success": True, "removed_home_user": removed_record})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "remove_user_from_home",
                "description": "Remove a user from a home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Identifier of the user to remove (cannot remove admin users or home owner).",
                        },
                    },
                    "required": ["home_name", "user_id"],
                },
            },
        }

