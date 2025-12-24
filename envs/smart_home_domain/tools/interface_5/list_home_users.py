import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListHomeUsers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        role: Optional[str] = None,
    ) -> str:
        """
        List users in a home, optionally filtered by role.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        home_users = data.get("home_users")
        users = data.get("users")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(home_users, dict):
            return json.dumps({"success": False, "error": "home_users store missing"})
        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "users store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})

        home_name = home_name.strip()
        
        # Find home by name
        home_id = None
        for hid, home in homes.items():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                break
        
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        role_filter = None
        if role:
            if not isinstance(role, str):
                return json.dumps({"success": False, "error": "role must be a string"})
            role_filter = role.strip().lower()
            if role_filter not in {"admin", "member", "guest"}:
                return json.dumps({"success": False, "error": "role must be one of admin, member, guest"})

        result_users = []
        for home_user_id, home_user in home_users.items():
            if home_user.get("home_id") == home_id:
                if role_filter and home_user.get("role") != role_filter:
                    continue
                
                user_id = home_user.get("user_id")
                user = users.get(user_id, {})
                
                result_users.append({
                    "home_user_id": home_user_id,
                    "user_id": user_id,
                    "email": user.get("email"),
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                    "role": home_user.get("role"),
                    "access_expires_at": home_user.get("access_expires_at"),
                    "status": user.get("status"),
                })

        return json.dumps({"success": True, "users": result_users})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_home_users",
                "description": "List all users associated with a home, optionally filtered by role.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "role": {
                            "type": "string",
                            "description": "Optional role filter; allowed values: admin, member, guest.",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }

