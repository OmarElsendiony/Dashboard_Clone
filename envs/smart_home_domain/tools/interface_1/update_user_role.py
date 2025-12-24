import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateUserRole(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        role: Optional[str] = None,
        access_expires_at: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        homes = data.get("homes", {})
        home_users = data.get("home_users", {})
        users = data.get("users", {})

        timestamp = "2025-12-19T23:59:00"
        if home_name and not home_id:
            for h_id, home in homes.items():
                if home.get("home_name") == home_name:
                    home_id = h_id
                    break
        if role and role.lower() not in ["guest", "member"]:
            return json.dumps({"success": False, "error": "Invalid role specified"})
            # Search by user_email if provided
        user = None
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

        target_home = homes.get(home_id)
        if not target_home or not user:
            return json.dumps({"success": False, "error": "Home or user not found"})

        home_user_record = next(
            (
                hu
                for hu in home_users.values()
                if hu.get("home_id") == home_id
                and hu.get("user_id") == user.get("user_id")
            ),
            None,
        )

        if home_user_record:
            # update existing record
            home_user_record["role"] = (
                role.lower() if role else home_user_record.get("role")
            )
            home_user_record["access_expires_at"] = (
                access_expires_at
                if role and role.lower() == "guest"
                else home_user_record.get("access_expires_at")
            )
            home_user_record["updated_at"] = timestamp
            return json.dumps(
                {
                    "success": True,
                    "message": "User role updated successfully.",
                    "home_user": home_user_record,
                }
            )
        else:
            # return error if no existing record
            return json.dumps(
                {"success": False, "error": "User is not a member of the home"}
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_user_role",
                "description": "Update a user's role in a smart home.",
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
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user whose role is to be updated.",
                        },
                        "user_email": {
                            "type": "string",
                            "description": "The email of the user whose role is to be updated.",
                        },
                        "role": {
                            "type": "string",
                            "description": "The new role assigned to the user (e.g., 'guest', 'member').",
                        },
                        "access_expires_at": {
                            "type": "string",
                            "description": "The expiration date for guest access (if applicable).",
                        },
                    },
                    "required": [],
                },
            },
        }
