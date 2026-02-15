import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetBranchDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_id: Optional[str] = None,
        repository_id: Optional[str] = None,
        branch_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([branch_id, branch_name]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one parameter must be provided: branch_id or branch_name",
                }
            )

        if branch_name and not repository_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "repository_id must be provided when using branch_name",
                }
            )

        branches = data.get("branches", {})

        target_branch = None

        if branch_id:
            if str(branch_id) in branches:
                target_branch = branches[str(branch_id)]
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Branch with id '{branch_id}' not found",
                    }
                )
        else:
            repositories = data.get("repositories", {})
            if str(repository_id) not in repositories:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with id '{repository_id}' not found",
                    }
                )

            branch_name_lower = str(branch_name).strip().lower()
            for branch in branches.values():
                if str(branch.get("repository_id")) != str(repository_id):
                    continue
                db_branch_name_lower = str(branch.get("branch_name") or "").lower()
                if db_branch_name_lower == branch_name_lower:
                    target_branch = branch
                    break

            if not target_branch:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Branch '{branch_name}' not found in repository '{repository_id}'",
                    }
                )

        return json.dumps({"success": True, "branch": target_branch})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_branch_details",
                "description": "Get detailed information about a specific branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "string",
                            "description": "Branch identifier",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Branch name (matched case-insensitively)",
                        },
                    },
                    "required": [],
                    "oneOf": [
                        {"required": ["branch_id"]},
                        {
                            "required": ["branch_name", "repository_id"]
                        },
                    ],
                },
            },
        }
