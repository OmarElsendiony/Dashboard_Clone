import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class InviteUserToHome(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        new_user_email: str,
        role: str,
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
        access_expires_at: Optional[str] = None,
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        homes = data.get("homes", {})
        home_users = data.get("home_users", {})
        users = data.get("users", {})
        target_home = None
        next_home_user_id = generate_id(home_users)
        timestamp = "2025-12-19T23:59:00"
        if not home_name and not home_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Provide home information. home name or home id",
                }
            )
        if home_name and not home_id:
            for h_id, home in homes.items():
                if home.get("home_name") == home_name:
                    home_id = h_id
                    break
        target_home = homes.get(home_id)
        if role and role.lower() not in ["guest", "member"]:
            return json.dumps({"success": False, "error": "Invalid role specified"})

        # validate new user email
        new_user = next(
            (
                user
                for user in users.values()
                if new_user_email and user.get("email") == new_user_email.lower()
            ),
            None,
        )
        if not target_home or not new_user:
            return json.dumps({"success": False, "error": "Home or user not found"})
        # Invite user to home
        user_record = {
            "home_user_id": str(next_home_user_id),
            "home_id": home_id,
            "user_id": new_user.get("user_id"),
            "role": role.lower() if role else None,
            "access_expires_at": (
                access_expires_at if role and role.lower() == "guest" else None
            ),
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        home_users[next_home_user_id] = user_record
        return json.dumps(
            {
                "success": True,
                "message": "User added to home successfully.",
                "invitation": user_record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "invite_user_to_home",
                "description": "Invite a user to a smart home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The unique identifier of the home to be updated.",
                        },
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home to be updated.",
                        },
                        "new_user_email": {
                            "type": "string",
                            "description": "The email of the user to be invited.",
                        },
                        "role": {
                            "type": "string",
                            "description": "The role assigned to the invited user (e.g., 'guest', 'member').",
                        },
                        "access_expires_at": {
                            "type": "string",
                            "description": "The duration of the user's access (e.g., '2025-12-19').",
                        },
                    },
                    "required": ["new_user_email", "role"],
                },
            },
        }
