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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({"success": False, "error": "Invalid data format"})
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

            b = branch
            results.append({
                "branch_id": str(b.get("branch_id", "")),
                "repository_id": str(b.get("repository_id", "")),
                "branch_name": str(b.get("branch_name", "")),
                "source_branch_name": str(b["source_branch_name"]) if b.get("source_branch_name") is not None else None,
                "commit_sha": str(b.get("commit_sha", "")),
                "linked_ticket_id": str(b["linked_ticket_id"]) if b.get("linked_ticket_id") is not None else None,
                "created_by": str(b["created_by"]) if b.get("created_by") is not None else None,
                "status": str(b.get("status", "")),
                "created_at": str(b.get("created_at", "")),
                "updated_at": str(b.get("updated_at", "")),
            })

        return json.dumps({
            "success": bool(True),
            "branches": results,
            "count": int(len(results)),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_branches",
                "description": "Lists branches in a repository, optionally filtered by branch name or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier. Use this or repository_name to target the repository.",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Repository name. Use this or repository_id to target the repository.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Filter results to branches matching this name (case-insensitive).",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter results by branch status.",
                            "enum": ["active", "deleted"],
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["repository_id"]},
                        {"required": ["repository_name"]},
                    ],
                },
            },
        }
