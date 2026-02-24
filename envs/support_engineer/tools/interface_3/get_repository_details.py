import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetRepositoryDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
    ) -> str:
        if not repository_name:
            return json.dumps({"error": "repository_name is required"})

        repositories = data.get("repositories", {})

        repository_details = None
        for _, repo in repositories.items():
            if repo.get("repository_name") == str(repository_name):
                repository_details = repo
                break

        if not repository_details:
            return json.dumps({"error": f"Repository with name '{repository_name}' not found"})

        return json.dumps({
            "success": True,
            "repository": {
                "repository_id": str(repository_details["repository_id"]),
                "repository_name": str(repository_details["repository_name"]),
                "description": str(repository_details["description"]) if repository_details.get("description") else None,
                "default_branch": str(repository_details["default_branch"]),
                "created_at": str(repository_details["created_at"]),
                "updated_at": str(repository_details["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_repository_details",
                "description": "Retrieves details of a repository using its name. It should be used when information about a specific repository is needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository",
                        },
                    },
                    "required": ["repository_name"],
                },
            },
        }
