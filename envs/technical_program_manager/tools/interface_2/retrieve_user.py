import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class RetrieveUser(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        username: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if (not username and not user_id) or (username and user_id):
            return json.dumps({
                "success": False,
                "error": "Exactly one of 'username' or 'user_id' must be provided"
            })

        users_dict = data.get("users", {})
        if not isinstance(users_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'users' must be a dict"
            })

        user_match = None
        matched_user_id = None

        if username:
            username_clean = str(username).strip()
            for uid, user_data in users_dict.items():
                if str(user_data.get("username", "")).strip() == username_clean:
                    user_match = user_data
                    matched_user_id = str(uid)
                    break

        if user_id:
            user_id_clean = str(user_id).strip()
            user_data = users_dict.get(user_id_clean)
            if user_data:
                user_match = user_data
                matched_user_id = str(user_id_clean)

        if not user_match:
            return json.dumps({
                "success": False,
                "error": "User not found"
            })

        users_projects = []

        project_members = data.get("project_members", {})
        projects = data.get("projects", {})

        if isinstance(project_members, dict) and isinstance(projects, dict):

            for pm in project_members.values():

                if str(pm.get("user_id")) == str(matched_user_id):

                    pid = str(pm.get("project_id"))
                    project_data = projects.get(pid)

                    if project_data:
                        users_projects.append({
                            "project_id": str(pid),
                            "project_name": str(project_data.get("project_name", ""))
                        })

        response_user = {
            "user_id": str(matched_user_id),
            "username": str(user_match.get("username", "")),
            "email": str(user_match.get("email", "")),
            "first_name": str(user_match.get("first_name", "")),
            "last_name": str(user_match.get("last_name", "")),
            "role": str(user_match.get("role", "")),
            "status": str(user_match.get("status", "")),
            "created_at": str(user_match.get("created_at", "")),
            "updated_at": str(user_match.get("updated_at", "")),
            "users_projects": list(users_projects)
        }

        return json.dumps({
            "success": bool(True),
            "user": response_user
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_user",
                "description": "Retrieves user profile information including role, account status and project memberships. "
                    "This function is used to validate that a user exists and confirm their assigned role before executing TPM operations. "
                    "Use this at the start of authentication workflows, when verifying project ownership, before assigning tasks, "
                    "or during escalation and communication steps that require confirmed user identity.",

                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "The unique username of the user to retrieve."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to retrieve."
                        }
                    },
                    "required": [],
                    "oneOf": [
                        {"required": ["username"]},
                        {"required": ["user_id"]}
                    ]
                }
            }
        }
