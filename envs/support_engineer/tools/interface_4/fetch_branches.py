import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchBranches(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        repository_name: Optional[str] = None,
        branch_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([repository_id, repository_name]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one repository identifier must be provided: repository_id or repository_name",
                }
            )

        if status is not None:
            valid_statuses = ["active", "deleted"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Valid values: active, deleted",
                    }
                )

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})

        target_repo_id = None

        if repository_id:
            if str(repository_id) not in repositories:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with id '{repository_id}' not found",
                    }
                )
            target_repo_id = str(repository_id)
        else:
            repository_name_lower = str(repository_name).strip().lower()
            for repo in repositories.values():
                db_name_lower = str(repo.get("repository_name") or "").lower()
                if db_name_lower == repository_name_lower:
                    target_repo_id = str(repo.get("repository_id"))
                    break
            if not target_repo_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with name '{repository_name}' not found",
                    }
                )

        results = []
        for branch in branches.values():
            if str(branch.get("repository_id")) != target_repo_id:
                continue

            if branch_name is not None:
                branch_name_lower = str(branch_name).strip().lower()
                db_branch_name_lower = str(branch.get("branch_name") or "").lower()
                if db_branch_name_lower != branch_name_lower:
                    continue

            if status is not None and branch.get("status") != status:
                continue

            results.append(branch)

        return json.dumps({"success": True, "branches": results, "count": len(results)})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_branches",
                "description": "List branches in a repository, optionally filtered by name or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Repository name",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Filter by branch name",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by branch status",
                            "enum": ["active",  "deleted"],
                        },
                    },
                    "required": [],
                    "oneOf": [
                        {"required": ["repository_id"]},
                        {"required": ["repository_name"]},
                    ],
                },
            },
        }
