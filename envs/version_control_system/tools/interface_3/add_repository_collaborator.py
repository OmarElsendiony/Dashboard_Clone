import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddRepositoryCollaborator(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        user_id: str,
        permission_level: str,
        status: str
    ) -> str:
        """
        Adds a collaborator to a repository in the version control system.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to add repository collaborator"})
        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required to add repository collaborator"})
        if not permission_level:
            return json.dumps({"success": False, "error": "permission_level is required to add repository collaborator"})
        if not status:
            return json.dumps({"success": False, "error": "status is required to add repository collaborator"})

        # Validate permission_level
        valid_permission_levels = ["read", "write", "admin"]
        if permission_level not in valid_permission_levels:
            return json.dumps({"success": False, "error": f"Invalid permission_level '{permission_level}'. Valid values: read, write, admin"})

        # Validate status
        valid_statuses = ["active", "pending", "removed"]
        if status not in valid_statuses:
            return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: active, pending, removed"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        repository_collaborators = data.get("repository_collaborators", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Validate user exists
        if str(user_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{user_id}' not found"})

        # Check if collaborator already exists for this repository and user
        for collab_id, collab in repository_collaborators.items():
            if (str(collab.get("repository_id")) == str(repository_id) and
                str(collab.get("user_id")) == str(user_id)):
                return json.dumps({"success": False, "error": f"User '{user_id}' is already a collaborator on repository '{repository_id}'"})

        # Generate new collaborator_id
        if repository_collaborators:
            max_id = max(int(k) for k in repository_collaborators.keys())
            new_id = str(max_id + 1)
        else:
            new_id = "1"

        # Create collaborator record
        new_collaborator = {
            "collaborator_id": new_id,
            "repository_id": repository_id,
            "user_id": user_id,
            "permission_level": permission_level,
            "status": status,
            "added_at": "2026-01-01T23:59:00",
        }

        repository_collaborators[new_id] = new_collaborator

        return json.dumps({"success": True, "result": new_collaborator})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_repository_collaborator",
                "description": "Adds a collaborator to a repository in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to add the collaborator to."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to add as a collaborator."
                        },
                        "permission_level": {
                            "type": "string",
                            "description": "The level of access granted to the collaborator. Valid values: read, write, admin."
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the collaborator invitation. Valid values: active, pending, removed."
                        }
                    },
                    "required": ["repository_id", "user_id", "permission_level", "status"]
                }
            }
        }
