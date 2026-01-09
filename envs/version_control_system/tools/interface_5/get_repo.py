import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetRepo(Tool):
    """Tool for retrieving repository details from the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_name: str,
    ) -> str:
        """
        Retrieve repository details by repository name.

        Args:
            data: The data dictionary containing all version control system data.
            repo_name: The name of the repository to look up (required).

        Returns:
            JSON string containing the success status and repository data if found.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})

        if not isinstance(repo_name, str) or not repo_name.strip():
            return json.dumps({"success": False, "error": "repo_name must be provided"})

        repo_name = repo_name.strip()

        # Search for repository by name
        found_repo = None
        for _, repo in repositories.items():
            if repo.get("repository_name") == repo_name:
                found_repo = repo.copy()
                break

        if not found_repo:
            return json.dumps({
                "success": False,
                "error": f"Repository with name '{repo_name}' not found"
            })

        # Build the response with all relevant repository information
        repo_data = {
            "repository_id": found_repo.get("repository_id"),
            "repository_name": found_repo.get("repository_name"),
            "owner_type": found_repo.get("owner_type"),
            "owner_id": found_repo.get("owner_id"),
            "description": found_repo.get("description"),
            "default_branch": found_repo.get("default_branch"),
            "is_fork": found_repo.get("is_fork"),
            "parent_repository_id": found_repo.get("parent_repository_id"),
            "is_archived": found_repo.get("is_archived"),
            "forks_count": found_repo.get("forks_count"),
            "license_type": found_repo.get("license_type"),
            "created_at": found_repo.get("created_at"),
            "updated_at": found_repo.get("updated_at"),
            "pushed_at": found_repo.get("pushed_at"),
        }

        return json.dumps({
            "success": True,
            "repo_data": repo_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the get_repo function."""
        return {
            "type": "function",
            "function": {
                "name": "get_repo",
                "description": "Retrieves detailed information about a repository from the version control system by its name. Use this to verify repository existence, check repository accessibility, or retrieve repository metadata for other operations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "The name of the repository to look up.",
                        },
                    },
                    "required": ["repo_name"],
                },
            },
        }
