import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool


class UpdateWorkspace(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        workspace_id: str,
        workspace_name: Optional[str] = None,
        description: Optional[str] = None,
        is_forking_allowed: Optional[bool] = None,
        is_private: Optional[bool] = None,
    ) -> str:
        """Update workspace information."""
        timestamp = "2026-01-01T23:59:00"

        def check_workspace_name_uniqueness(
            workspaces_dict: Dict[str, Any],
            workspace_name_str: str,
            workspace_id_str: str,
        ) -> Tuple[bool, Optional[str]]:
            """Check if workspace name is unique, excluding current workspace."""
            for wid, workspace in workspaces_dict.items():
                if str(wid) == workspace_id_str:
                    continue

                if str(workspace.get("workspace_name", "")).strip() == workspace_name_str and workspace.get("owner_id") == workspaces_dict[workspace_id_str].get("owner_id"):
                    return (
                        False,
                        f"Workspace with name '{workspace_name_str}' already exists (workspace_id: {wid})",
                    )

            return True, None

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        # Check at least one update parameter is provided
        if (
            not workspace_name
            and not description
            and is_forking_allowed is None
            and is_private is None
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one of workspace_name, description, is_forking_allowed, or is_private must be provided for update",
                }
            )

        workspaces_dict = data.get("workspaces", {})

        workspace_id_str = str(workspace_id).strip()
        workspace_name_str = str(workspace_name).strip() if workspace_name else None

        # Check if workspace exists
        if workspace_id_str not in workspaces_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Workspace with ID '{workspace_id_str}' not found",
                }
            )

        workspace = workspaces_dict[workspace_id_str]

        # Check workspace name uniqueness if provided
        if workspace_name_str:
            is_valid, error_msg = check_workspace_name_uniqueness(
                workspaces_dict, workspace_name_str, workspace_id_str
            )
            if not is_valid:
                return json.dumps({"success": False, "error": error_msg})
            workspace["workspace_name"] = workspace_name_str

        if description is not None:
            workspace["description"] = str(description).strip()

        if is_forking_allowed is not None:
            workspace["is_forking_allowed"] = bool(is_forking_allowed)

        if is_private is not None:
            workspace["is_private"] = bool(is_private)

        workspace["updated_at"] = timestamp

        workspace_return = workspace.copy()
        workspace_return["workspace_id"] = workspace_id_str

        return json.dumps(
            {
                "success": True,
                "workspace": workspace_return,
                "message": f"Workspace '{workspace.get('workspace_name')}' updated successfully",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the update_workspace function."""
        return {
            "type": "function",
            "function": {
                "name": "update_workspace",
                "description": (
                    "Update workspace information including name, description, forking permissions, and privacy settings. "
                    "At least one of workspace_name, description, is_forking_allowed, or is_private must be provided for update. "
                    "Validates that the workspace exists. "
                    "If workspace_name is provided, ensures it's unique for an owner (excluding the current workspace). "
                    "Returns the updated workspace details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workspace_id": {
                            "type": "string",
                            "description": "The ID of the workspace to update.",
                        },
                        "workspace_name": {
                            "type": "string",
                            "description": "Optional. The new name for the workspace. Must be unique for an owner.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. The new description for the workspace.",
                        },
                        "is_forking_allowed": {
                            "type": "boolean",
                            "description": "Optional. Whether forking repositories in this workspace is allowed.",
                        },
                        "is_private": {
                            "type": "boolean",
                            "description": "Optional. Whether the workspace is private.",
                        },
                    },
                    "required": ["workspace_id"],
                },
            },
        }
