import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool


class GetProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        workspace_id: str,
        user_id: str,
        project_name: str,
    ) -> str:
        """Retrieve project information by workspace_id and project_name, include member details for user_id."""
        def find_project(projects_dict: Dict[str, Any], workspace_id_str: str, project_name_str: str) -> Optional[Dict[str, Any]]:
            """Find project by workspace_id and project_name."""
            for pid, project in projects_dict.items():
                if str(project.get("workspace_id")) == workspace_id_str and str(project.get("project_name", "")).strip() == project_name_str:
                    project_info = project.copy()
                    project_info["project_id"] = str(pid)
                    return project_info
            
            return None

        def find_member_details(project_members_dict: Dict[str, Any], project_id: str, user_id_str: str) -> Optional[Dict[str, Any]]:
            """Find project member details for a specific user in a project."""
            for member_id, member in project_members_dict.items():
                if str(member.get("project_id")) == project_id and str(member.get("user_id")) == user_id_str:
                    member_info = member.copy()
                    member_info["project_member_id"] = str(member_id)
                    return member_info
            return None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        projects_dict = data.get("projects", {})
        project_members_dict = data.get("project_members", {})

        # Convert to strings
        workspace_id_str = str(workspace_id).strip()
        user_id_str = str(user_id).strip()
        project_name_str = str(project_name).strip()

        # Find project
        project = find_project(projects_dict, workspace_id_str, project_name_str)

        if not project:
            return json.dumps({
                "success": False,
                "error": f"Project '{project_name_str}' not found in workspace '{workspace_id_str}'"
            })

        # Find member details for user_id
        member_details = find_member_details(
            project_members_dict,
            project["project_id"],
            user_id_str
        )
        project["member_details"] = member_details

        return json.dumps({
            "success": True,
            "project": project,
            "message": f"Project '{project_name_str}' found in workspace '{workspace_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the get_project function."""
        return {
            "type": "function",
            "function": {
                "name": "get_project",
                "description": (
                    "Retrieve project information by workspace_id and project_name. "
                    "Returns complete project details including project_id, workspace_id, organization_id, "
                    "project_key, project_name, status, description, is_private, and timestamps. "
                    "Also includes project member details (role, status) for the specified user_id. "
                    "The member_details field will be null if the user is not a member of that project. "
                    "Returns an error if workspace_id, user_id, or project_name is not provided or if the project is not found."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workspace_id": {
                            "type": "string",
                            "description": "The ID of the workspace containing the project.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user whose project member details to retrieve.",
                        },
                        "project_name": {
                            "type": "string",
                            "description": "The name of the project to retrieve.",
                        },
                    },
                    "required": ["workspace_id", "user_id", "project_name"],
                },
            },
        }