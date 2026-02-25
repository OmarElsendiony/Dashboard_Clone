import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AssignProjectMembers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        user_id: str,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not project_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'project_id'"
            })

        if not user_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'user_id'"
            })

        projects_dict = data.get("projects", {})
        users_dict = data.get("users", {})
        project_members_dict = data.get("project_members", {})

        if not isinstance(projects_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'projects' must be a dict"
            })

        if not isinstance(users_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'users' must be a dict"
            })

        if not isinstance(project_members_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'project_members' must be a dict"
            })

        project_id_clean = str(project_id).strip()
        user_id_clean = str(user_id).strip()

        if project_id_clean not in projects_dict:
            return json.dumps({
                "success": False,
                "error": f"Project with ID '{project_id_clean}' not found",
            })

        user_data = users_dict.get(user_id_clean)
        if not user_data:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id_clean}' not found"
            })

        if str(user_data.get("status", "")).strip() != "active":
            return json.dumps({
                "success": False,
                "error": "Cannot assign inactive user to project"
            })

        for member in project_members_dict.values():
            if (
                str(member.get("project_id", "")).strip() == project_id_clean and
                str(member.get("user_id", "")).strip() == user_id_clean
            ):
                return json.dumps({
                    "success": False,
                    "error": "User is already assigned to this project"
                })

        new_project_member_id = generate_id(project_members_dict)

        joined_at = timestamp

        project_members_dict[new_project_member_id] = {
            "project_member_id": str(new_project_member_id),
            "project_id": str(project_id_clean),
            "user_id": str(user_id_clean),
            "joined_at": joined_at
        }

        response_membership = {
            "project_member_id": str(new_project_member_id),
            "project_id": str(project_id_clean),
            "user_id": str(user_id_clean),
            "joined_at": joined_at
        }

        return json.dumps({
            "success": True,
            "project_member": response_membership
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_project_members",
                "description": "Assigns an active user to a project by creating a project membership entry. "
                               "This function validates that the project and user exist and prevents duplicate assignments. "
                               "Use this before formally adding the user to the project team during project intake and setup workflows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to be assigned to the project."
                        }
                    },
                    "required": ["project_id", "user_id"]
                }
            }
        }
