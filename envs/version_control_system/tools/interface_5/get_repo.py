import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetRepo(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_name: str,
    ) -> str:

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
        return {
            "type": "function",
            "function": {
                "name": "get_repo",
                "description": "Retrieves detailed information about a repository.",
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
