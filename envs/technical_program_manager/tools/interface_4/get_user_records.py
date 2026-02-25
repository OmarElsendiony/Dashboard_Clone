import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetUserRecords(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        username: Optional[str] = None,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([username, user_id, email, role, status]):
            return json.dumps({
                "success": False,
                "error": "At least one filter parameter must be provided",
            })

        if role is not None:
            role_str = str(role).strip()
            valid_roles = ["technical_program_manager", "stakeholder", "collaborator"]
            if role_str not in valid_roles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid role '{role_str}'. Valid values: {', '.join(valid_roles)}",
                    }
                )
        else:
            role_str = None

        if status is not None:
            status_str = str(status).strip()
            valid_statuses = ["active", "inactive"]
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )
        else:
            status_str = None

        username_str = str(username).strip() if username else None
        user_id_str = str(user_id).strip() if user_id else None
        email_str = str(email).strip() if email else None

        users = data.get("users", {})
        project_members = data.get("project_members", {})

        results = []
        for user in users.values():
            if user_id_str is not None and str(user.get("user_id", "")) != user_id_str:
                continue

            if username_str is not None and username_str.lower() != str(user.get("username", "")).lower():
                continue

            if email_str is not None and email_str.lower() != str(user.get("email", "")).lower():
                continue

            if role_str is not None and str(user.get("role", "")) != role_str:
                continue

            if status_str is not None and str(user.get("status", "")) != status_str:
                continue

            user_projects = []
            for pm in project_members.values():
                if str(pm.get("user_id", "")) == str(user.get("user_id", "")):
                    user_projects.append({"project_id": str(pm.get("project_id", ""))})
            user_projects.sort(key=lambda x: int(x["project_id"]))

            filtered_user = {
                "user_id": str(user.get("user_id", "")),
                "username": str(user.get("username", "")),
                "email": str(user.get("email", "")),
                "role": str(user.get("role", "")),
                "status": str(user.get("status", "")),
                "created_at": str(user.get("created_at", "")),
                "updated_at": str(user.get("updated_at", "")),
                "projects": user_projects,
            }
            results.append(filtered_user)
        results.sort(key=lambda x: int(x["user_id"]))
        return json.dumps({"success": True, "users": results, "count": int(len(results))})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user_records",
                "description": "Retrieves user records and associated project memberships based on optional filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Filter by username (exact, case-insensitive).",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Filter by the exact unique user identifier (user_id).",
                        },
                        "email": {
                            "type": "string",
                            "description": "Filter by email (exact, case-insensitive).",
                        },
                        "role": {
                            "type": "string",
                            "description": "Filter by user role",
                            "enum": [
                                "technical_program_manager",
                                "stakeholder",
                                "collaborator",
                            ],
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by user status",
                            "enum": ["active", "inactive"],
                        },
                    },
                    "anyOf": [
                        {"required": ["username"]},
                        {"required": ["user_id"]},
                        {"required": ["email"]},
                        {"required": ["role"]},
                        {"required": ["status"]},
                    ],
                    "required": [],
                },
            },
        }
