import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class DeleteBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_id: Optional[str] = None,
        branch_name: Optional[str] = None,
        repository_id: Optional[str] = None,
        repository_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([branch_id, branch_name]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one branch identifier must be provided: branch_id or branch_name",
                }
            )

        if not any([repository_id, repository_name]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one repository identifier must be provided: repository_id or repository_name",
                }
            )

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        pull_requests = data.get("pull_requests", {})

        target_repo_id = None
        target_repo = None

        if repository_id:
            if str(repository_id) not in repositories:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with id '{repository_id}' not found",
                    }
                )
            target_repo_id = str(repository_id)
            target_repo = repositories[target_repo_id]
        else:
            for repo in repositories.values():
                if repo.get("repository_name") == repository_name:
                    target_repo_id = str(repo.get("repository_id"))
                    target_repo = repo
                    break
            if not target_repo:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with name '{repository_name}' not found",
                    }
                )

        target_branch = None

        if branch_id:
            if str(branch_id) in branches:
                target_branch = branches[str(branch_id)]
                if str(target_branch.get("repository_id")) != target_repo_id:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Branch '{branch_id}' does not belong to the specified repository",
                        }
                    )
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Branch with id '{branch_id}' not found",
                    }
                )
        else:
            for branch in branches.values():
                if (
                    str(branch.get("repository_id")) == target_repo_id
                    and branch.get("branch_name") == branch_name
                ):
                    target_branch = branch
                    break

            if not target_branch:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Branch '{branch_name}' not found in repository '{target_repo_id}'",
                    }
                )

        if target_branch.get("branch_name") == target_repo.get("default_branch"):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot delete default branch '{target_branch.get('branch_name')}'",
                }
            )

        for pr in pull_requests.values():
            if (
                pr.get("source_branch_name") == target_branch.get("branch_name")
                and str(pr.get("repository_id")) == target_repo_id
                and pr.get("status") == "open"
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot delete branch '{target_branch.get('branch_name')}'. There are open pull requests sourced from this branch",
                    }
                )

        static_timestamp = "2026-02-02 23:59:00"

        target_branch["status"] = "deleted"
        target_branch["updated_at"] = static_timestamp

        return json.dumps({"success": True, "branch": target_branch})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_branch",
                "description": "Deletes a branch from a repository. At least one branch identifier must be provided: branch id or branch name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "string",
                            "description": "Branch identifier",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Branch name",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Repository name",
                        },
                    },
                    "required": [],
                    "oneOf": [
                        {"required": ["branch_id"]},
                        {"required": ["branch_name"]},
                    ],
                    "anyOf": [
                        {"required": ["repository_id"]},
                        {"required": ["repository_name"]},
                     ],
                },
            },
        }
