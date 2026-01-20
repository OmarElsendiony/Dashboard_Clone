import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateBranchInRepo(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_name: str,
        source_branch: str,
        commit_sha: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to create branch"})
        if not branch_name:
            return json.dumps({"success": False, "error": "branch_name is required to create branch"})
        if not source_branch:
            return json.dumps({"success": False, "error": "source_branch is required to create branch"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        commits = data.get("commits", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Check if branch name already exists in this repository
        for branch_id, branch in branches.items():
            if (str(branch.get("repository_id")) == str(repository_id) and
                branch.get("branch_name") == branch_name):
                return json.dumps({"success": False, "error": f"Branch '{branch_name}' already exists in repository '{repository_id}'"})

        # Find source branch and get its commit_sha
        source_branch_data = None
        for branch_id, branch in branches.items():
            if (str(branch.get("repository_id")) == str(repository_id) and
                branch.get("branch_name") == source_branch):
                source_branch_data = branch
                break

        if source_branch_data is None:
            return json.dumps({"success": False, "error": f"Source branch '{source_branch}' not found in repository '{repository_id}'"})

        # Determine the commit_sha to use
        if commit_sha is None:
            # Use the source branch's current commit_sha (can be None if source has no commits)
            final_commit_sha = source_branch_data.get("commit_sha", None)
        else:
            # Validate the specified commit_sha exists
            commit_found = False
            for commit_id, commit in commits.items():
                if commit.get("commit_sha") == commit_sha:
                    # Also validate commit belongs to the same repository
                    if str(commit.get("repository_id")) != str(repository_id):
                        return json.dumps({"success": False, "error": f"Commit with SHA '{commit_sha}' does not belong to repository '{repository_id}'"})
                    commit_found = True
                    break

            if not commit_found:
                return json.dumps({"success": False, "error": f"Commit with SHA '{commit_sha}' not found"})

            final_commit_sha = commit_sha

        # Generate new branch_id
        if branches:
            max_id = max(int(k) for k in branches.keys())
            new_id = str(max_id + 1)
        else:
            new_id = "1"

        # Create branch record
        new_branch = {
            "branch_id": new_id,
            "repository_id": repository_id,
            "branch_name": branch_name,
            "commit_sha": final_commit_sha,
            "source_branch": source_branch_data.get("branch_id"),
            "is_default": False,
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00"
        }

        branches[new_id] = new_branch

        return json.dumps({"success": True, "result": new_branch})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_branch_in_repo",
                "description": "Creates a new branch in a repository from a source branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to create the branch in."
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name for the new branch. Must be unique within the repository."
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "The name of the branch to create the new branch from."
                        },
                        "commit_sha": {
                            "type": "string",
                            "description": "The SHA hash of a specific commit to point the new branch to. If not provided, uses the source branch's current commit (optional)."
                        }
                    },
                    "required": ["repository_id", "branch_name", "source_branch"]
                }
            }
        }
