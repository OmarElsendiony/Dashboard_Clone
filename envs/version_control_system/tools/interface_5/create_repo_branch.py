import json
import hashlib
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRepoBranch(Tool):
    """Tool for creating a new branch in a repository in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        branch_name: str,
        base_branch: Optional[str] = None,
    ) -> str:
        """
        Create a new branch in a repository.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository to create the branch in (required).
            branch_name: The name of the new branch to create (required).
            base_branch: The name of the base branch to create from (optional).
                        If provided, the new branch inherits the commit SHA from this branch.
                        If not provided, the branch is created from the default branch.

        Returns:
            str: A JSON-encoded string containing the success status and created branch data.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """
            Generates a new unique ID for a record.

            Returns:
                str: The new unique ID as a string.
            """
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        def generate_commit_sha(repo_name: str, branch_name: str, timestamp: str) -> str:
            """
            Generates a unique commit SHA for a branch.

            Returns:
                str: A 40-character hexadecimal SHA string.
            """
            content = f"{repo_name}:{branch_name}:{timestamp}:new-branch"
            return hashlib.sha1(content.encode()).hexdigest()

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})

        # Validate required fields
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not branch_name:
            return json.dumps({"success": False, "error": "Missing required parameter: branch_name"})

        if not isinstance(branch_name, str) or not branch_name.strip():
            return json.dumps({"success": False, "error": "branch_name must be a non-empty string"})

        branch_name = branch_name.strip()
        repo_id = str(repo_id).strip()

        # Validate repository exists
        repo = None
        for r_id, r in repositories.items():
            if str(r.get("repository_id")) == repo_id:
                repo = r
                break

        if not repo:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Check if repository is archived
        if repo.get("is_archived"):
            return json.dumps({
                "success": False,
                "error": f"Cannot create branch in archived repository '{repo.get('repository_name')}'"
            })

        # Check if branch name already exists in this repository
        for _, branch in branches.items():
            if (
                str(branch.get("repository_id")) == repo_id
                and branch.get("branch_name") == branch_name
            ):
                return json.dumps({
                    "success": False,
                    "error": f"Branch '{branch_name}' already exists in repository '{repo.get('repository_name')}'"
                })

        # Find the base branch to inherit commit SHA from
        source_branch = None
        source_branch_id = None

        if base_branch is not None:
            if not isinstance(base_branch, str) or not base_branch.strip():
                return json.dumps({"success": False, "error": "base_branch must be a non-empty string if provided"})

            base_branch = base_branch.strip()

            # Find the base branch by name in this repository
            for branch_id, branch in branches.items():
                if (
                    str(branch.get("repository_id")) == repo_id
                    and branch.get("branch_name") == base_branch
                ):
                    source_branch = branch
                    source_branch_id = branch_id
                    break

            if not source_branch:
                return json.dumps({
                    "success": False,
                    "error": f"Base branch '{base_branch}' not found in repository '{repo.get('repository_name')}'"
                })
        else:
            # No base_branch provided, use the default branch
            default_branch_name = repo.get("default_branch", "main")

            for branch_id, branch in branches.items():
                if (
                    str(branch.get("repository_id")) == repo_id
                    and branch.get("branch_name") == default_branch_name
                ):
                    source_branch = branch
                    source_branch_id = branch_id
                    break

            if not source_branch:
                return json.dumps({
                    "success": False,
                    "error": f"Default branch '{default_branch_name}' not found in repository '{repo.get('repository_name')}'. Cannot create branch without a base."
                })

        # Set timestamp for created_at and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Generate new branch ID
        new_branch_id = generate_id(branches)

        # Get the commit SHA from the source branch
        commit_sha = source_branch.get("commit_sha")

        # If source branch doesn't have a commit SHA, generate one
        if not commit_sha:
            commit_sha = generate_commit_sha(repo.get("repository_name", ""), branch_name, timestamp)

        # Create new branch record
        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": repo_id,
            "branch_name": branch_name,
            "commit_sha": commit_sha,
            "source_branch": source_branch_id,
            "is_default": False,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add the new branch to the branches dictionary
        branches[new_branch_id] = new_branch

        return json.dumps({
            "success": True,
            "message": f"Branch '{branch_name}' created successfully in repository '{repo.get('repository_name')}'",
            "branch_data": new_branch
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the create_repo_branch function."""
        return {
            "type": "function",
            "function": {
                "name": "create_repo_branch",
                "description": "Creates a new branch in a repository in the version control system. The new branch inherits the commit SHA (HEAD pointer) from the base branch. If no base_branch is provided, the branch is created from the repository's default branch. The new branch is not set as default. Use this after confirming the repository exists using get_repo, the user has admin or write access using get_repo_permissions, the base branch exists using get_repo_branch, and the new branch name is not already taken using get_repo_branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository to create the branch in. Required field. The repository must exist and not be archived.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the new branch to create. Required field and must be unique within the repository.",
                        },
                        "base_branch": {
                            "type": "string",
                            "description": "The name of the base branch to create the new branch from. Optional - if not provided, the repository's default branch is used. The base branch must exist in the repository.",
                        },
                    },
                    "required": ["repo_id", "branch_name"],
                },
            },
        }
