import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class WriteRepoPermissions(Tool):
    """Tool for adding, updating, or removing repository collaborator permissions."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        repo_id: str,
        user_id: str,
        permission_level: Optional[str] = None,
    ) -> str:
        """
        Add, update, or remove repository collaborator permissions.

        Args:
            data: The data dictionary containing all version control system data.
            action: The action to perform. Must be one of: "upsert" (add or update), "remove".
            repo_id: The ID of the repository (required).
            user_id: The ID of the user to manage permissions for (required).
            permission_level: The permission level to assign. Must be one of: read, write, admin.
                            Required for "upsert" action, optional for "remove" action.

        Returns:
            JSON string containing the success status and collaborator data.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """
            Generates a new unique ID for a record.

            Returns:
                str: The new unique ID as a string.
            """
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        users = data.get("users", {})

        # Validate action
        if not action or not isinstance(action, str):
            return json.dumps({"success": False, "error": "action is required and must be a string"})
        action = action.strip().lower()

        allowed_actions = {"upsert", "remove"}
        if action not in allowed_actions:
            return json.dumps({
                "success": False,
                "error": f"action must be one of: {', '.join(sorted(allowed_actions))}"
            })

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

        # Check if user is the owner of the repository (cannot modify owner permissions)
        owner_id = str(repo.get("owner_id", ""))
        if owner_id == user_id:
            return json.dumps({
                "success": False,
                "error": f"Cannot modify permissions for repository owner. User '{user_id}' is the owner of repository '{repo_id}'"
            })

        # Find existing collaborator record
        existing_collaborator_key = None
        existing_collaborator = None
        for key, collab in repository_collaborators.items():
            if (
                str(collab.get("repository_id")) == repo_id
                and str(collab.get("user_id")) == user_id
            ):
                existing_collaborator_key = key
                existing_collaborator = collab
                break

        timestamp = "2026-01-01T23:59:00"

        if action == "upsert":
            # Validate permission_level is required for upsert
            if not permission_level or not isinstance(permission_level, str) or not permission_level.strip():
                return json.dumps({
                    "success": False,
                    "error": "permission_level is required for 'upsert' action"
                })
            permission_level = permission_level.strip().lower()

            allowed_permission_levels = {"read", "write", "admin"}
            if permission_level not in allowed_permission_levels:
                return json.dumps({
                    "success": False,
                    "error": f"permission_level must be one of: {', '.join(sorted(allowed_permission_levels))}"
                })

            if existing_collaborator:
                # Update existing collaborator
                existing_collaborator["permission_level"] = permission_level
                existing_collaborator["status"] = "active"

                return json.dumps({
                    "success": True,
                    "message": f"Collaborator permissions updated successfully",
                    "action_performed": "updated",
                    "collaborator_data": existing_collaborator
                })
            else:
                # Create new collaborator
                new_collaborator_id = generate_id(repository_collaborators)

                new_collaborator = {
                    "collaborator_id": new_collaborator_id,
                    "repository_id": repo_id,
                    "user_id": user_id,
                    "permission_level": permission_level,
                    "status": "active",
                    "added_at": timestamp,
                }

                repository_collaborators[new_collaborator_id] = new_collaborator

                return json.dumps({
                    "success": True,
                    "message": f"Collaborator added successfully",
                    "action_performed": "created",
                    "collaborator_data": new_collaborator
                })

        elif action == "remove":
            if not existing_collaborator:
                return json.dumps({
                    "success": False,
                    "error": f"User '{user_id}' is not a collaborator on repository '{repo_id}'"
                })

            # Check if already removed
            current_status = existing_collaborator.get("status", "").lower()
            if current_status == "removed":
                return json.dumps({
                    "success": False,
                    "error": f"User '{user_id}' has already been removed from repository '{repo_id}'"
                })

            # Remove collaborator by setting status to "removed"
            existing_collaborator["status"] = "removed"

            return json.dumps({
                "success": True,
                "message": f"Collaborator removed successfully",
                "action_performed": "removed",
                "collaborator_data": existing_collaborator
            })

        # Should not reach here due to action validation above
        return json.dumps({"success": False, "error": "Unknown error occurred"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the write_repo_permissions function."""
        return {
            "type": "function",
            "function": {
                "name": "write_repo_permissions",
                "description": "Add, update, or remove repository collaborator permissions. Use action='upsert' to add a new collaborator or update an existing collaborator's permission level. Use action='remove' to remove a collaborator from the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform. Must be one of: 'upsert' (add or update collaborator), 'remove' (remove collaborator).",
                        },
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository to manage permissions for.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user to manage permissions for.",
                        },
                        "permission_level": {
                            "type": "string",
                            "description": "The permission level to assign. Must be one of: 'read', 'write', 'admin'. Required for 'upsert' action.",
                        },
                    },
                    "required": ["action", "repo_id", "user_id"],
                },
            },
        }
