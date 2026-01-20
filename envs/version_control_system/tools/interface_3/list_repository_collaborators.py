import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListRepositoryCollaborators(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        user_id: Optional[str] = None,
        permission_level: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to list repository collaborators"})

        # Validate permission_level if provided
        if permission_level is not None:
            valid_permission_levels = ["read", "write", "admin"]
            if permission_level not in valid_permission_levels:
                return json.dumps({"success": False, "error": f"Invalid permission_level '{permission_level}'. Valid values: read, write, admin"})

        # Validate status if provided
        if status is not None:
            valid_statuses = ["active", "pending", "removed"]
            if status not in valid_statuses:
                return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: active, pending, removed"})

        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Find all collaborators for this repository
        collaborators = []
        for collab_id, collab in repository_collaborators.items():
            if str(collab.get("repository_id")) == str(repository_id):
                # Apply user_id filter if provided
                if user_id is not None and str(collab.get("user_id")) != str(user_id):
                    continue
                # Apply permission_level filter if provided
                if permission_level is not None and collab.get("permission_level") != permission_level:
                    continue
                # Apply status filter if provided
                if status is not None and collab.get("status") != status:
                    continue
                collaborators.append(collab)

        return json.dumps({"success": True, "result": collaborators})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_repository_collaborators",
                "description": "Lists all collaborators for a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to list collaborators for."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Optional filter to return only the collaborator record for this specific user (optional)."
                        },
                        "permission_level": {
                            "type": "string",
                            "description": "Optional filter to return only collaborators with this permission level. Valid values: read, write, admin (optional)."
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional filter to return only collaborators with this status. Valid values: active, pending, removed (optional)."
                        }
                    },
                    "required": ["repository_id"]
                }
            }
        }
