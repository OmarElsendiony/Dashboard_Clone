import json
import hashlib
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRepo(Tool):
    """Tool for creating a new repository in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        owner_id: str,
        repo_name: str,
        default_branch: str = "main",
        description: Optional[str] = None,
    ) -> str:
        """
        Create a new repository in the version control system.

        Args:
            data: The data dictionary containing all version control system data.
            owner_id: The ID of the user who will own the repository (required).
            repo_name: The name of the repository (required, must be unique).
            default_branch: The name of the default branch (default: main).
            description: The description of the repository (optional).

        Returns:
            str: A JSON-encoded string containing the success status and created repository data.
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
            Generates a unique commit SHA for the initial commit.

            Returns:
                str: A 40-character hexadecimal SHA string.
            """
            content = f"{repo_name}:{branch_name}:{timestamp}:initial"
            return hashlib.sha1(content.encode()).hexdigest()

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        branches = data.get("branches", {})
        repository_collaborators = data.get("repository_collaborators", {})

        # Validate required fields
        if not owner_id:
            return json.dumps({"success": False, "error": "Missing required parameter: owner_id"})

        if not repo_name:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_name"})

        if not isinstance(repo_name, str) or not repo_name.strip():
            return json.dumps({"success": False, "error": "repo_name must be a non-empty string"})

        repo_name = repo_name.strip()

        # Validate owner exists
        owner_id = str(owner_id)
        if owner_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{owner_id}' not found"
            })

        owner = users[owner_id]

        # Check if owner is active
        if owner.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{owner_id}' is not active"
            })

        # Check if repository name already exists
        for _, repo in repositories.items():
            if repo.get("repository_name") == repo_name:
                return json.dumps({
                    "success": False,
                    "error": f"Repository with name '{repo_name}' already exists"
                })

        # Validate default_branch
        if not isinstance(default_branch, str) or not default_branch.strip():
            default_branch = "main"
        else:
            default_branch = default_branch.strip()

        # Generate new repository ID
        new_repo_id = generate_id(repositories)

        # Set timestamp for created_at and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Create new repository record
        new_repo = {
            "repository_id": new_repo_id,
            "owner_type": "user",
            "owner_id": owner_id,
            "repository_name": repo_name,
            "description": description.strip() if description else "",
            "default_branch": default_branch,
            "is_fork": False,
            "parent_repository_id": None,
            "is_archived": False,
            "forks_count": 0,
            "license_type": "unlicensed",
            "created_at": timestamp,
            "updated_at": timestamp,
            "pushed_at": timestamp,
        }

        # Add the new repository to the repositories dictionary
        repositories[new_repo_id] = new_repo

        # Create the default branch for the repository
        new_branch_id = generate_id(branches)
        initial_commit_sha = generate_commit_sha(repo_name, default_branch, timestamp)

        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": new_repo_id,
            "branch_name": default_branch,
            "commit_sha": initial_commit_sha,
            "source_branch": None,
            "is_default": True,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add the new branch to the branches dictionary
        branches[new_branch_id] = new_branch

        # Add the owner as an admin collaborator
        new_collaborator_id = generate_id(repository_collaborators)

        new_collaborator = {
            "collaborator_id": new_collaborator_id,
            "repository_id": new_repo_id,
            "user_id": owner_id,
            "permission_level": "admin",
            "status": "active",
            "added_at": timestamp,
        }

        # Add the new collaborator to the repository_collaborators dictionary
        repository_collaborators[new_collaborator_id] = new_collaborator

        return json.dumps({
            "success": True,
            "message": f"Repository '{repo_name}' created successfully",
            "repo_data": new_repo,
            "branch_data": new_branch,
            "collaborator_data": new_collaborator
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the create_repo function."""
        return {
            "type": "function",
            "function": {
                "name": "create_repo",
                "description": "Creates a new repository in the version control system with the specified name and default branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner_id": {
                            "type": "string",
                            "description": "The ID of the user who will own the repository.",
                        },
                        "repo_name": {
                            "type": "string",
                            "description": "The name of the repository to create.",
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "The name of the default branch to create. Defaults to 'main'.",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the repository.",
                        },
                    },
                    "required": ["owner_id", "repo_name"],
                },
            },
        }
