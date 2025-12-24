import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class InviteUser(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        email: str,
        role: str,
        access_expires_at: Optional[str] = None,
    ) -> str:
        """
        Add a user to a home with a specified role.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        def validate_timestamp(ts: str) -> bool:
            if not isinstance(ts, str):
                return False
            parts = ts.split("T")
            if len(parts) != 2:
                return False
            date_parts = parts[0].split("-")
            if len(date_parts) != 3:
                return False
            try:
                year, month, day = map(int, date_parts)
                return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31
            except ValueError:
                return False

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

        if not isinstance(email, str) or not email.strip():
            return json.dumps({"success": False, "error": "email must be provided"})
        email = email.strip().lower()

        # Find user by email
        user_id = None
        user = None
        for uid, u in users.items():
            if u.get("email", "").strip().lower() == email:
                user_id = uid
                user = u
                break
        
        if not user_id:
            return json.dumps({"success": False, "error": f"User with email '{email}' not found"})

        if user.get("status") != "active":
            return json.dumps({"success": False, "error": f"User with email '{email}' is not active"})

        if not isinstance(role, str) or not role.strip():
            return json.dumps({"success": False, "error": "role must be provided"})
        role = role.strip().lower()

        # Per SOP: only guest and member roles can be assigned via invite
        if role not in {"member", "guest"}:
            return json.dumps({"success": False, "error": "role must be one of member, guest"})

        for home_user in home_users.values():
            if home_user.get("home_id") == home_id and home_user.get("user_id") == user_id:
                return json.dumps({"success": False, "error": f"User with email '{email}' is already a member of home '{home_name}'"})

        expires_at = None
        if access_expires_at:
            if not validate_timestamp(access_expires_at):
                return json.dumps({"success": False, "error": "access_expires_at must be in format YYYY-MM-DDTHH:MM:SS"})
            expires_at = access_expires_at

        home_user_id = generate_id(home_users)
        timestamp = "2025-12-19T23:59:00"

        record = {
            "home_user_id": home_user_id,
            "home_id": home_id,
            "user_id": user_id,
            "role": role,
            "access_expires_at": expires_at,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        home_users[home_user_id] = record

        return json.dumps({"success": True, "home_user": record})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "invite_user",
                "description": "Invite a user to a home with a specific role. Only member and guest roles can be assigned.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address of the user to invite.",
                        },
                        "role": {
                            "type": "string",
                            "description": "Role for the user; allowed values: member, guest.",
                        },
                        "access_expires_at": {
                            "type": "string",
                            "description": "Optional expiration timestamp for guest access in format YYYY-MM-DDTHH:MM:SS.",
                        },
                    },
                    "required": ["home_name", "email", "role"],
                },
            },
        }

