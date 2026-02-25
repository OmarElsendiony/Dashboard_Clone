import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListUsers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for users"}
            )

        # Require at least one filter parameter
        if all(
            param is None
            for param in [user_id, role, status, email, first_name, last_name]
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one filter parameter is required (user_id, role, status, email, first_name, or last_name)",
                }
            )

        if role is not None:
            valid_roles = [
                "collaborator",
                "stakeholder",
                "technical_program_manager",
            ]
            if role not in valid_roles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}",
                    }
                )

        if status is not None:
            valid_statuses = ["active", "inactive"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )

        users = data.get("users", {})

        # If user_id is provided, return that specific user
        if user_id is not None:
            user = None
            user_key_str = str(user_id)

            if user_key_str in users:
                user_data = users[user_key_str]
                if str(user_data.get("user_id")) == str(user_id):
                    user = user_data.copy()

            if not user:
                for _user_key, user_data in users.items():
                    if str(user_data.get("user_id")) == str(user_id):
                        user = user_data.copy()
                        break

            if not user:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID {str(user_id)} not found",
                    }
                )

            # If additional filters are provided alongside user_id, enforce them
            if role is not None and user.get("role") != role:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID {str(user_id)} does not have role '{role}'",
                    }
                )

            if status is not None and user.get("status") != status:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID {str(user_id)} does not have status '{status}'",
                    }
                )

            if email is not None:
                user_email = user.get("email", "").lower()
                if user_email != email.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"User with ID {str(user_id)} does not have email '{email}'",
                        }
                    )

            if first_name is not None:
                user_first_name = user.get("first_name", "").lower()
                if user_first_name != first_name.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"User with ID {str(user_id)} does not have first_name '{first_name}'",
                        }
                    )

            if last_name is not None:
                user_last_name = user.get("last_name", "").lower()
                if user_last_name != last_name.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"User with ID {str(user_id)} does not have last_name '{last_name}'",
                        }
                    )

            # Explicit type casting for all fields
            user["user_id"] = str(user.get("user_id"))
            user["role"] = str(user.get("role"))
            user["status"] = str(user.get("status"))
            user["email"] = str(user.get("email"))
            user["first_name"] = str(user.get("first_name"))
            user["last_name"] = str(user.get("last_name"))
            user["created_at"] = str(user.get("created_at"))
            user["updated_at"] = str(user.get("updated_at"))

            return json.dumps(
                {
                    "success": True,
                    "count": 1,
                    "users": [user],
                }
            )

        results = []

        for _user_key, user in users.items():
            if role is not None:
                if user.get("role") != role:
                    continue

            if status is not None:
                if user.get("status") != status:
                    continue

            if email is not None:
                user_email = user.get("email", "").lower()
                if user_email != email.lower():
                    continue

            if first_name is not None:
                user_first_name = user.get("first_name", "").lower()
                if user_first_name != first_name.lower():
                    continue

            if last_name is not None:
                user_last_name = user.get("last_name", "").lower()
                if user_last_name != last_name.lower():
                    continue

            user_copy = user.copy()
            # Explicit type casting for all fields
            user_copy["user_id"] = str(user_copy.get("user_id"))
            user_copy["role"] = str(user_copy.get("role"))
            user_copy["status"] = str(user_copy.get("status"))
            user_copy["email"] = str(user_copy.get("email"))
            user_copy["first_name"] = str(user_copy.get("first_name"))
            user_copy["last_name"] = str(user_copy.get("last_name"))
            user_copy["created_at"] = str(user_copy.get("created_at"))
            user_copy["updated_at"] = str(user_copy.get("updated_at"))

            results.append(user_copy)

        return json.dumps(
            {
                "success": True,
                "count": len(results),
                "users": results,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_users",
                "description": "List and filter users. Requires at least one filter parameter (user_id, role, status, email, first_name, or last_name). Use this to find users, check user roles and status, identify team members, and validate user existence.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Filter by specific user ID",
                        },
                        "role": {
                            "type": "string",
                            "description": "Filter users by role",
                            "enum": [
                                "collaborator",
                                "stakeholder",
                                "technical_program_manager",
                            ],
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter users by status",
                            "enum": ["active", "inactive"],
                        },
                        "email": {
                            "type": "string",
                            "description": "Filter users by email address (case-insensitive)",
                        },
                        "first_name": {
                            "type": "string",
                            "description": "Filter users by first name (case-insensitive)",
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Filter users by last name (case-insensitive)",
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["user_id"]},
                        {"required": ["role"]},
                        {"required": ["status"]},
                        {"required": ["email"]},
                        {"required": ["first_name"]},
                        {"required": ["last_name"]},
                    ],
                },
            },
        }
