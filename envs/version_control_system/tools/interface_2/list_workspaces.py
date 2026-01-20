import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListWorkspaces(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        owner_id: str,
        workspace_name: str,
        user_id: Optional[str] = None,
    ) -> str:
        """List workspace by owner_id and workspace_name, return workspace member details for user_id."""

        def find_workspace(
            workspaces_dict: Dict[str, Any], owner_id_str: str, workspace_name_str: str
        ) -> Optional[Dict[str, Any]]:
            """Find workspace by owner_id and workspace_name."""
            for wid, workspace in workspaces_dict.items():
                if (
                    str(workspace.get("owner_id")) == owner_id_str
                    and str(workspace.get("workspace_name", "")).strip()
                    == workspace_name_str
                ):
                    workspace_info = workspace.copy()
                    workspace_info["workspace_id"] = str(wid)
                    return workspace_info
            return None

        def find_member_details(
            workspace_members_dict: Dict[str, Any], workspace_id: str, user_id_str: str
        ) -> Optional[Dict[str, Any]]:
            """Find workspace member details for a specific user in a workspace."""
            for member_id, member in workspace_members_dict.items():
                if (
                    str(member.get("workspace_id")) == workspace_id
                    and str(member.get("user_id")) == user_id_str
                ):
                    member_info = member.copy()
                    member_info["workspace_member_id"] = str(member_id)
                    return member_info

            return None

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        # # Validate required parameters
        if not owner_id:
            return json.dumps({"success": False, "error": "owner_id is required"})

        if not workspace_name:
            return json.dumps({"success": False, "error": "workspace_name is required"})

        # Get data containers
        workspaces_dict = data.get("workspaces", {})
        workspace_members_dict = data.get("workspace_members", {})

        # Convert to strings and set user_id to owner_id if not provided
        owner_id_str = str(owner_id).strip()
        workspace_name_str = str(workspace_name).strip()
        user_id_str = str(user_id).strip() if user_id else owner_id_str

        # Find workspace by owner_id and workspace_name
        workspace = find_workspace(workspaces_dict, owner_id_str, workspace_name_str)

        if not workspace:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Workspace '{workspace_name_str}' not found for owner_id '{owner_id_str}'",
                }
            )

        # Add member details for user_id
        member_details = find_member_details(
            workspace_members_dict, workspace["workspace_id"], user_id_str
        )
        workspace["member_details"] = member_details

        return json.dumps(
            {
                "success": True,
                "workspace": workspace,
                "message": f"Workspace '{workspace_name_str}' found for owner '{owner_id_str}'",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the list_workspaces function."""
        return {
            "type": "function",
            "function": {
                "name": "list_workspaces",
                "description": "Retrieves a specific workspace by owner and name with member details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner_id": {
                            "type": "string",
                            "description": "The ID of the user who owns the workspace.",
                        },
                        "workspace_name": {
                            "type": "string",
                            "description": "The name of the workspace to retrieve.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "(optional) The ID of the user whose workspace member details to retrieve. Defaults to owner_id if not provided.",
                        },
                    },
                    "required": ["owner_id", "workspace_name"],
                },
            },
        }
