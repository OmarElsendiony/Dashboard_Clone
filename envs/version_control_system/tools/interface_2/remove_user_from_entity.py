import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class RemoveUserFromEntity(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        target_user_id: str,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> str:
        """Remove a user from a workspace, project, or repository."""

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

        target_user_id_str = str(target_user_id).strip()
        target_user = users_dict[target_user_id_str]

        # Handle workspace removal
        if workspace_id:
            workspace_id_str = str(workspace_id).strip()
            
            member_id_to_remove = None
            for wm_id, member in workspace_members_dict.items():
                if str(member.get("workspace_id")) == workspace_id_str and str(member.get("user_id")) == target_user_id_str:
                    member_id_to_remove = wm_id
                    break

            if not member_id_to_remove:
                return json.dumps({
                    "success": False,
                    "error": f"User '{target_user.get('username')}' is not a member of workspace '{workspace_id_str}'",
                })

            removed_member = workspace_members_dict.pop(member_id_to_remove)

            return json.dumps({
                "success": True,
                "removed_member": removed_member,
                "message": f"User '{target_user.get('username')}' removed from workspace successfully",
            })

        # Handle project removal
        if project_id:
            project_id_str = str(project_id).strip()

            member_id_to_remove = None
            for pm_id, member in project_members_dict.items():
                if str(member.get("project_id")) == project_id_str and str(member.get("user_id")) == target_user_id_str:
                    member_id_to_remove = pm_id
                    break

            if not member_id_to_remove:
                return json.dumps({
                    "success": False,
                    "error": f"User '{target_user.get('username')}' is not a member of project '{project_id_str}'",
                })

            removed_member = project_members_dict.pop(member_id_to_remove)

            return json.dumps({
                "success": True,
                "removed_member": removed_member,
                "message": f"User '{target_user.get('username')}' removed from project successfully",
            })

        # Handle repository removal
        if repository_id:
            repository_id_str = str(repository_id).strip()

            collaborator_id_to_remove = None
            for rc_id, collaborator in repository_collaborators_dict.items():
                if str(collaborator.get("repository_id")) == repository_id_str and str(collaborator.get("user_id")) == target_user_id_str:
                    collaborator_id_to_remove = rc_id
                    break

            if not collaborator_id_to_remove:
                return json.dumps({
                    "success": False,
                    "error": f"User '{target_user.get('username')}' is not a collaborator of repository '{repository_id_str}'",
                })

            removed_collaborator = repository_collaborators_dict.pop(collaborator_id_to_remove)

            return json.dumps({
                "success": True,
                "removed_collaborator": removed_collaborator,
                "message": f"User '{target_user.get('username')}' removed from repository successfully",
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the remove_user_from_entity function."""
        return {
            "type": "function",
            "function": {
                "name": "remove_user_from_entity",
                "description": "Removes a user from a workspace, project, or repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_user_id": {
                            "type": "string",
                            "description": "The ID of the user to remove from the entity.",
                        },
                        "workspace_id": {
                            "type": "string",
                            "description": "The ID of the workspace to remove the user from (optional).",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The ID of the project to remove the user from (optional).",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository to remove the user from (optional).",
                        },
                    },
                    "required": ["target_user_id"],
                },
            },
        }
