import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetUsers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        role: Optional[str] = None,
        technical_expertise: Optional[str] = None,
        limit: int = 5,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if status is not None:
            valid_statuses = ["active", "inactive"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Valid values: active, inactive",
                    }
                )

        if role is not None:
            valid_roles = ["technical_engineer", "support_engineer"]
            if role not in valid_roles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid role '{role}'. Valid values: technical_engineer, support_engineer",
                    }
                )

        if technical_expertise is not None:
            valid_expertise = [
                "db_admin",
                "frontend_dev",
                "backend_dev",
                "security_specialist",
            ]
            if technical_expertise not in valid_expertise:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid technical_expertise '{technical_expertise}'. Valid values: db_admin, frontend_dev, backend_dev, security_specialist",
                    }
                )

        users = data.get("users", {})

        results = []
        for user in users.values():
            if user_id is not None and str(user.get("user_id")) != str(user_id):
                continue

            if first_name is not None and first_name.lower() not in user.get(
                "first_name", ""
            ).lower():
                continue

            if last_name is not None and last_name.lower() not in user.get(
                "last_name", ""
            ).lower():
                continue

            if email is not None and email.lower() not in user.get("email", "").lower():
                continue

            if status is not None and user.get("status") != status:
                continue

            if role is not None and user.get("role") != role:
                continue

            if technical_expertise is not None:
                user_expertise = user.get("technical_expertise")
                if user_expertise != technical_expertise:
                    continue

            filtered_user = {
                "user_id": user.get("user_id"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "email": user.get("email"),
                "status": user.get("status"),
                "role": user.get("role"),
                "technical_expertise": user.get("technical_expertise"),
                "created_at": user.get("created_at"),
            }
            results.append(filtered_user)

        if limit is not None and limit > 0:
            results = results[:limit]

        return json.dumps({"success": True, "users": results, "count": len(results)})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_users",
                "description": "List support team members by identifier, name, email, status, role, or technical expertise.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Filter by user identifier",
                        },
                        "first_name": {
                            "type": "string",
                            "description": "Filter by first name substring",
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Filter by last name substring",
                        },
                        "email": {
                            "type": "string",
                            "description": "Filter by email substring",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by user status",
                            "enum": ["active", "inactive"],
                        },
                        "role": {
                            "type": "string",
                            "description": "Filter by user role",
                            "enum": ["technical_engineer", "support_engineer"],
                        },
                        "technical_expertise": {
                            "type": "string",
                            "description": "Filter by technical expertise area",
                            "enum": [
                                "db_admin",
                                "frontend_dev",
                                "backend_dev",
                                "security_specialist",
                            ],
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of users to return",
                        },
                    },
                    "required": [],
                },
            },
        }
