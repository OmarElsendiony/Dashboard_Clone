import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetRepoBranch(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        branch_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})

        # Validate repo_id
        if not repo_id or not str(repo_id).strip():
            return json.dumps({"success": False, "error": "repo_id must be provided"})
        repo_id = str(repo_id).strip()

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

        # If branch_name is provided, find that specific branch
        if branch_name is not None:
            if not isinstance(branch_name, str) or not branch_name.strip():
                return json.dumps({"success": False, "error": "branch_name must be a non-empty string if provided"})

            branch_name = branch_name.strip()

            # Search for the specific branch
            found_branch = None
            for _, branch in branches.items():
                if (
                    str(branch.get("repository_id")) == repo_id
                    and branch.get("branch_name") == branch_name
                ):
                    found_branch = branch.copy()
                    break

            if not found_branch:
                return json.dumps({
                    "success": False,
                    "error": f"Branch '{branch_name}' not found in repository '{repo_id}'"
                })

            # Build the response for a single branch
            branch_data = {
                "branch_id": found_branch.get("branch_id"),
                "repository_id": found_branch.get("repository_id"),
                "branch_name": found_branch.get("branch_name"),
                "commit_sha": found_branch.get("commit_sha"),
                "source_branch": found_branch.get("source_branch"),
                "is_default": found_branch.get("is_default"),
                "created_at": found_branch.get("created_at"),
                "updated_at": found_branch.get("updated_at"),
            }

            return json.dumps({
                "success": True,
                "branch_data": branch_data
            })

        # If branch_name is not provided, return all branches for the repository
        repo_branches = []
        for _, branch in branches.items():
            if str(branch.get("repository_id")) == repo_id:
                branch_data = {
                    "branch_id": branch.get("branch_id"),
                    "repository_id": branch.get("repository_id"),
                    "branch_name": branch.get("branch_name"),
                    "commit_sha": branch.get("commit_sha"),
                    "source_branch": branch.get("source_branch"),
                    "is_default": branch.get("is_default"),
                    "created_at": branch.get("created_at"),
                    "updated_at": branch.get("updated_at"),
                }
                repo_branches.append(branch_data)

        if not repo_branches:
            return json.dumps({
                "success": False,
                "error": f"No branches found for repository '{repo_id}'"
            })

        # Sort branches: default branch first, then alphabetically by name
        repo_branches.sort(key=lambda b: (not b.get("is_default", False), b.get("branch_name", "")))

        return json.dumps({
            "success": True,
            "count": len(repo_branches),
            "branches": repo_branches
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_repo_branch",
                "description": "Retrieves branch information from a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository to look up branches for. Required field.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the branch to look up. Optional - if not provided, returns all branches for the repository.",
                        },
                    },
                    "required": ["repo_id"],
                },
            },
        }
