import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddUserToEntity(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        target_user_id: str,
        role: str,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> str:
        """Add a user to a workspace, project, or repository."""
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Check exactly one entity ID is provided
        entity_ids = [workspace_id, project_id, repository_id]
        if sum(1 for eid in entity_ids if eid) != 1:
            return json.dumps({
                "success": False,
                "error": "Exactly one of workspace_id, project_id, or repository_id must be provided",
            })

        # Get data containers
        users_dict = data.get("users", {})
        workspace_members_dict = data.get("workspace_members", {})
        project_members_dict = data.get("project_members", {})
        repository_collaborators_dict = data.get("repository_collaborators", {})

        # Convert to strings
        target_user_id_str = str(target_user_id).strip()
        role_str = str(role).strip()

        target_user = users_dict[target_user_id_str]

        # Handle workspace addition
        if workspace_id:
            workspace_id_str = str(workspace_id).strip()
            
            valid_roles = ["Admin", "User"]
            if role_str not in valid_roles:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid role '{role_str}' for workspace. Must be one of: {', '.join(valid_roles)}",
                })

            # Check if user already exists in workspace
            for member in workspace_members_dict.values():
                if str(member.get("workspace_id")) == workspace_id_str and str(member.get("user_id")) == target_user_id_str:
                    return json.dumps({
                        "success": False,
                        "error": f"User '{target_user.get('username')}' is already a member of workspace '{workspace_id_str}'",
                    })

            new_member_id = generate_id(workspace_members_dict)
            workspace_members_dict[new_member_id] = {
                "workspace_member_id": new_member_id,
                "workspace_id": workspace_id_str,
                "user_id": target_user_id_str,
                "roles": role_str,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            return json.dumps({
                "success": True,
                "workspace_member": workspace_members_dict[new_member_id],
                "message": f"User '{target_user.get('username')}' added to workspace with role '{role_str}'",
            })

        # Handle project addition
        if project_id:
            project_id_str = str(project_id).strip()
            
            valid_roles = ["Build_Administrator", "Contributor", "Project Administrator", "Reader", "Release_Administrator"]
            if role_str not in valid_roles:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid role '{role_str}' for project. Must be one of: {', '.join(valid_roles)}",
                })

            # Check if user already exists in project
            for member in project_members_dict.values():
                if str(member.get("project_id")) == project_id_str and str(member.get("user_id")) == target_user_id_str:
                    return json.dumps({
                        "success": False,
                        "error": f"User '{target_user.get('username')}' is already a member of project '{project_id_str}'",
                    })

            new_member_id = generate_id(project_members_dict)
            project_members_dict[new_member_id] = {
                "project_member_id": new_member_id,
                "project_id": project_id_str,
                "user_id": target_user_id_str,
                "roles": role_str,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            return json.dumps({
                "success": True,
                "project_member": project_members_dict[new_member_id],
                "message": f"User '{target_user.get('username')}' added to project with role '{role_str}'",
            })

        # Handle repository addition
        if repository_id:
            repository_id_str = str(repository_id).strip()

            valid_roles = ["read", "write", "admin"]
            if role_str not in valid_roles:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid role '{role_str}' for repository. Must be one of: {', '.join(valid_roles)}",
                })

            # Check if user already exists in repository
            for collaborator in repository_collaborators_dict.values():
                if str(collaborator.get("repository_id")) == repository_id_str and str(collaborator.get("user_id")) == target_user_id_str:
                    return json.dumps({
                        "success": False,
                        "error": f"User '{target_user.get('username')}' is already a collaborator of repository '{repository_id_str}'",
                    })

            # Add user to repository
            new_collaborator_id = generate_id(repository_collaborators_dict)
            repository_collaborators_dict[new_collaborator_id] = {
                "collaborator_id": new_collaborator_id,
                "repository_id": repository_id_str,
                "user_id": target_user_id_str,
                "permission_level": role_str,
                "status": "active",
                "added_at": timestamp,
            }

            return json.dumps({
                "success": True,
                "repository_collaborator": repository_collaborators_dict[new_collaborator_id],
                "message": f"User '{target_user.get('username')}' added to repository with permission '{role_str}'",
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the add_user_to_entity function."""
        return {
            "type": "function",
            "function": {
                "name": "add_user_to_entity",
                "description": (
                    "Add a user to a workspace, project, or repository. "
                    "Exactly one of workspace_id, project_id, or repository_id must be provided. "
                    "For workspace: valid roles are 'Admin', 'User'. "
                    "For project: valid roles are 'Build_Administrator', 'Contributor', 'Project Administrator', 'Reader', 'Release_Administrator'. "
                    "For repository: valid roles are 'read', 'write', 'admin'. "
                    "Checks if the user is already a member/collaborator before adding. "
                    "Returns the created membership/collaborator record."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_user_id": {
                            "type": "string",
                            "description": "The ID of the user to add to the entity.",
                        },
                        "role": {
                            "type": "string",
                            "description": "The role/permission level to assign to the user. Valid values depend on entity type.",
                        },
                        "workspace_id": {
                            "type": "string",
                            "description": "Optional. The ID of the workspace to add the user to.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional. The ID of the project to add the user to.",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Optional. The ID of the repository to add the user to.",
                        },
                    },
                    "required": ["target_user_id", "role"],
                },
            },
        }
