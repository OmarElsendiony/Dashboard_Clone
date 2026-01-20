import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ModifyCollaboratorAccess(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        collaborator_id: str,
        permission_level: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not collaborator_id:
            return json.dumps({"success": False, "error": "collaborator_id is required to modify collaborator access"})

        if permission_level is None and status is None:
            return json.dumps({"success": False, "error": "At least one of permission_level or status must be provided for update"})

        repository_collaborators = data.get("repository_collaborators", {})

        # Validate collaborator exists
        if str(collaborator_id) not in repository_collaborators:
            return json.dumps({"success": False, "error": f"Collaborator with id '{collaborator_id}' not found"})

        collaborator = repository_collaborators[str(collaborator_id)]

        # Track if any actual change is made
        changes_made = False

        # Validate and update permission_level if provided
        if permission_level is not None:
            valid_permission_levels = ["read", "write", "admin"]
            if permission_level not in valid_permission_levels:
                return json.dumps({"success": False, "error": f"Invalid permission_level '{permission_level}'. Valid values: read, write, admin"})
            if collaborator.get("permission_level") != permission_level:
                collaborator["permission_level"] = permission_level
                changes_made = True

        # Validate and update status if provided
        if status is not None:
            valid_statuses = ["active", "pending", "removed"]
            if status not in valid_statuses:
                return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: active, pending, removed"})
            if collaborator.get("status") != status:
                collaborator["status"] = status
                changes_made = True

        if not changes_made:
            return json.dumps({"success": False, "error": "No changes made. The provided values are the same as the current values."})

        return json.dumps({"success": True, "result": collaborator})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_collaborator_access",
                "description": "Updates a repository collaborator's permission level or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collaborator_id": {
                            "type": "string",
                            "description": "The unique identifier of the collaborator record to update."
                        },
                        "permission_level": {
                            "type": "string",
                            "description": "The new permission level for the collaborator. Valid values: read, write, admin (optional)."
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status for the collaborator. Valid values: active, pending, removed (optional)."
                        }
                    },
                    "required": ["collaborator_id"]
                }
            }
        }
