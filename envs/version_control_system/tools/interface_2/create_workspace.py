import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool


class CreateWorkspace(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        owner_id: str,
        workspace_name: str,
        description: Optional[str] = None,
        is_private: Optional[bool] = True,
        is_forking_allowed: Optional[bool] = False,
    ) -> str:
        """Create a new workspace and workspace member in the system."""
        timestamp = "2026-01-01T23:59:00"

        def check_workspace_name_uniqueness(
            workspaces_dict: Dict[str, Any], workspace_name_str: str, owner_id_str: str
        ) -> Tuple[bool, Optional[str]]:
            """Check if workspace name is unique."""
            for wid, workspace in workspaces_dict.items():
                if (
                    str(workspace.get("workspace_name", "")).strip()
                    == workspace_name_str
                    and str(workspace.get("owner_id")) == owner_id_str
                ):
                    return (
                        False,
                        f"Workspace with name '{workspace_name_str}' already exists (workspace_id: {wid})",
                    )
            return True, None

        def check_free_plan_limit(
            workspaces_dict: Dict[str, Any], owner_id_str: str, owner_plan: str
        ) -> Tuple[bool, Optional[str]]:
            """Check if free plan user already has a workspace."""
            if owner_plan != "free":
                return True, None

            for workspace in workspaces_dict.values():
                if str(workspace.get("owner_id")) == owner_id_str:
                    return (
                        False,
                        f"User with free plan can only have 1 workspace. User '{owner_id_str}' already owns a workspace.",
                    )
            return True, None

        def generate_workspace_id(workspaces_dict: Dict[str, Any]) -> str:
            """Generate a new unique workspace ID."""
            if not workspaces_dict:
                return "1"
            return str(max(int(k) for k in workspaces_dict.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        workspaces_dict = data.get("workspaces", {})
        users_dict = data.get("users", {})        


        # Convert to strings for consistent comparison
        owner_id_str = str(owner_id).strip()
        workspace_name_str = str(workspace_name).strip()
        description_str = str(description).strip() if description else None
        is_private_bool = bool(is_private) if is_private is not None else True
        is_forking_allowed_bool = (
            bool(is_forking_allowed) if is_forking_allowed is not None else False
        )

        # Check workspace name uniqueness
        is_valid, error_msg = check_workspace_name_uniqueness(
            workspaces_dict, workspace_name_str, owner_id_str
        )
        if not is_valid:
            return json.dumps({"success": False, "error": error_msg})

        # Check free plan limit
        owner_info = users_dict.get(owner_id_str)
        owner_plan = str(owner_info.get("plan_type", "")).strip()
        is_valid, error_msg = check_free_plan_limit(
            workspaces_dict, owner_id_str, owner_plan
        )
        if not is_valid:
            return json.dumps({"success": False, "error": error_msg})

        # Generate new workspace ID
        new_workspace_id = generate_workspace_id(workspaces_dict)

        # Create new workspace entry
        new_workspace = {
            "workspace_id": new_workspace_id,
            "workspace_name": workspace_name_str,
            "owner_id": owner_id_str,
            "description": description_str,
            "is_forking_allowed": is_forking_allowed_bool,
            "is_private": is_private_bool,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        workspace_members_dict = data.get("workspace_members", {})
        new_workspace_member_id = generate_workspace_id(workspace_members_dict)
        
        new_workspace_member = {
            "workspace_member_id": new_workspace_member_id,
            "workspace_id": new_workspace_id,
            "user_id": owner_id_str,
            "roles": "Admin",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add to data
        workspaces_dict[new_workspace_id] = new_workspace
        workspace_members_dict[new_workspace_member_id] = new_workspace_member

        return json.dumps(
            {
                "success": True,
                "workspace": new_workspace,
                "workspace_member": new_workspace_member,
                "message": f"Workspace '{workspace_name_str}' successfully created with ID: {new_workspace_id}",
                "owner_username": owner_info.get("username"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the create_workspace function."""
        return {
            "type": "function",
            "function": {
                "name": "create_workspace",
                "description": (
                    "Create a new workspace and workspace member details in Bitbucket. "
                    "Ensures workspace_name is globally unique across all workspaces. "
                    "For users on free plan, enforces a limit of 1 workspace per user. "
                    "Premium users can create multiple workspaces. "
                    "Returns the created workspace and workspace member details including the generated workspace_id. "
                    "is_private defaults to true, is_forking_allowed defaults to false."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner_id": {
                            "type": "string",
                            "description": "The ID of the user who will own the workspace. Must be an active user.",
                        },
                        "workspace_name": {
                            "type": "string",
                            "description": "The name of the workspace. Must be unique for an owner.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. A description of the workspace's purpose.",
                        },
                        "is_private": {
                            "type": "boolean",
                            "description": "Optional. Whether the workspace is private. Defaults to true.",
                        },
                        "is_forking_allowed": {
                            "type": "boolean",
                            "description": "Optional. Whether forking repositories in this workspace is allowed. Defaults to false.",
                        },
                    },
                    "required": ["owner_id", "workspace_name"],
                },
            },
        }