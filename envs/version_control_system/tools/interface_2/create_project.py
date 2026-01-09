import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool


class CreateProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        workspace_id: str,
        project_key: str,
        project_name: str,
        is_private: bool,
        user_id: str,
        description: Optional[str] = None,
    ) -> str:
        """Create a new project in a workspace."""
        timestamp = "2026-01-01T23:59:00"

        def check_uniqueness(projects_dict: Dict[str, Any], workspace_id_str: str, project_key_str: str, project_name_str: str) -> Tuple[bool, Optional[str]]:
            """Check if project_key and project_name are unique within the workspace."""
            for pid, project in projects_dict.items():
                if str(project.get("workspace_id")) != workspace_id_str:
                    continue
                
                if str(project.get("project_key", "")).strip() == project_key_str:
                    return False, f"Project with key '{project_key_str}' already exists in workspace '{workspace_id_str}' (project_id: {pid})"
                
                if str(project.get("project_name", "")).strip() == project_name_str:
                    return False, f"Project with name '{project_name_str}' already exists in workspace '{workspace_id_str}' (project_id: {pid})"
            
            return True, None

        def generate_project_id(projects_dict: Dict[str, Any]) -> str:
            """Generate a new unique project ID."""
            if not projects_dict:
                return "1"
            return str(max(int(k) for k in projects_dict.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        projects_dict = data.get("projects", {})
        workspaces_dict = data.get("workspaces", {})

        workspace_id_str = str(workspace_id).strip()
        project_key_str = str(project_key).strip()
        project_name_str = str(project_name).strip()
        description_str = str(description).strip() if description else None
        is_private_bool = bool(is_private)

        # Check if workspace exists
        if workspace_id_str not in workspaces_dict:
            return json.dumps({
                "success": False,
                "error": f"Workspace with ID '{workspace_id_str}' not found"
            })

        # Check uniqueness
        is_valid, error_msg = check_uniqueness(projects_dict, workspace_id_str, project_key_str, project_name_str)
        if not is_valid:
            return json.dumps({"success": False, "error": error_msg})

        # Generate new project ID
        new_project_id = generate_project_id(projects_dict)

        new_project = {
            "project_id": new_project_id,
            "workspace_id": workspace_id_str,
            "organization_id": None,
            "project_key": project_key_str,
            "project_name": project_name_str,
            "status": "active",
            "description": description_str,
            "is_private": is_private_bool,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        projects_dict[new_project_id] = new_project

        project_members = []
        project_member_dict = data.get("project_members", {})
        new_project_member_id = generate_project_id(project_member_dict)
        new_project_member = {
            "project_member_id": new_project_member_id,
            "project_id": new_project_id,
            "user_id": user_id,
            "roles": "Project Administrator",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        project_member_dict[new_project_member_id] = new_project_member
        project_members.append(new_project_member)

        if user_id != workspaces_dict[workspace_id_str].get("owner_id"):
            owner_project_member_id = generate_project_id(project_member_dict)
            owner_project_member = {
                "project_member_id": owner_project_member_id,
                "project_id": new_project_id,
                "user_id": workspaces_dict[workspace_id_str].get("owner_id"),
                "roles": "Project Administrator",
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            project_member_dict[owner_project_member_id] = owner_project_member
            project_members.append(owner_project_member)

        return json.dumps({
            "success": True,
            "project": new_project,
            "project_member": project_members,
            "message": f"Project '{project_name_str}' successfully created with ID: {new_project_id}",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the create_project function."""
        return {
            "type": "function",
            "function": {
                "name": "create_project",
                "description": (
                    "Create a new project and project_member within a workspace."
                    "Validates that the workspace exists. "
                    "Ensures project_key is unique within the workspace. "
                    "Ensures project_name is unique within the workspace. "
                    "Returns the created project details including the generated project_id. "
                    "organization_id and status are always set to null."
                    "Creates a project member for the user and owner if they are different, both with Project Administrator role."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workspace_id": {
                            "type": "string",
                            "description": "The ID of the workspace where the project will be created.",
                        },
                        "project_key": {
                            "type": "string",
                            "description": "The unique key for the project within the workspace.",
                        },
                        "project_name": {
                            "type": "string",
                            "description": "The unique name for the project within the workspace.",
                        },
                        "is_private": {
                            "type": "boolean",
                            "description": "Whether the project is private.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user who will be the project administrator.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. A description of the project's purpose.",
                        },
                    },
                    "required": ["workspace_id", "project_key", "project_name", "is_private", "user_id"],
                },
            },
        }