import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetRepoPermissions(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        user_id: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        users = data.get("users", {})

        # Validate repo_id
        if not repo_id or not str(repo_id).strip():
            return json.dumps({"success": False, "error": "repo_id must be provided"})
        repo_id = str(repo_id).strip()

        # Validate user_id
        if not user_id or not str(user_id).strip():
            return json.dumps({"success": False, "error": "user_id must be provided"})
        user_id = str(user_id).strip()

        # Check if repository exists
        repo = None
        for _, r in repositories.items():
            if str(r.get("repository_id")) == repo_id:
                repo = r
                break

        if not repo:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Check if user exists
        user = None
        for _, u in users.items():
            if str(u.get("user_id")) == user_id:
                user = u
                break

        if not user:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id}' not found"
            })

        user_status = user.get("status", "unknown")

        # Check if user is the owner of the repository (owner has implicit admin access)
        owner_id = str(repo.get("owner_id", ""))
        if owner_id == user_id:
            return json.dumps({
                "success": True,
                "permission_data": {
                    "repository_id": repo_id,
                    "user_id": user_id,
                    "permission_level": "admin",
                    "is_owner": True,
                    "status": "active",
                    "user_status": user_status,
                }
            })

        # Check repository_collaborators for explicit permissions
        collaborator_record = None
        for _, collab in repository_collaborators.items():
            if (
                str(collab.get("repository_id")) == repo_id
                and str(collab.get("user_id")) == user_id
            ):
                collaborator_record = collab
                break

        if not collaborator_record:
            return json.dumps({
                "success": False,
                "error": f"User '{user_id}' does not have permissions on repository '{repo_id}'"
            })

        # Build the permission response
        permission_data = {
            "repository_id": repo_id,
            "user_id": user_id,
            "collaborator_id": collaborator_record.get("collaborator_id"),
            "permission_level": collaborator_record.get("permission_level"),
            "is_owner": False,
            "status": collaborator_record.get("status"),
            "user_status": user_status,
            "added_at": collaborator_record.get("added_at"),
        }

        return json.dumps({
            "success": True,
            "permission_data": permission_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:

        return {
            "type": "function",
            "function": {
                "name": "get_repo_permissions",
                "description": "Retrieves the permission level and collaboration status for a specific user on a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository to check permissions for.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user to check permissions for.",
                        },
                    },
                    "required": ["repo_id", "user_id"],
                },
            },
        }
