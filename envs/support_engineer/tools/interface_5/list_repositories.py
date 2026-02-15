import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class ListRepositories(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        repository_id: Optional[str] = None,
        repository_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for repositories"}
            )

        repositories = data.get("repositories", {})
        results = []

        for repo_id, repo_data in repositories.items():
            if repository_id and repo_id != repository_id:
                continue
            if repository_name:
                repo_name = repo_data.get("repository_name", "").lower()
                search_name = repository_name.lower()
                if search_name not in repo_name:
                    continue

            results.append({**repo_data, "repository_id": repo_id})

        results.sort(key=lambda x: x.get("repository_name", ""))

        return json.dumps(
            {
                "success": True,
                "count": len(results),
                "repositories": results,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "list_repositories",
                "description": "List available repositories to determine where fixes or investigations should occur. Use this to match issues to repositories based on error paths, service names, or feature ownership. Returns all repositories if no filters are provided, or filtered results when repository_id or repository_name is specified. Repository names support partial matching to help identify relevant repositories by service name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by exact repository_id (optional)",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Filter by repository name (supports partial matching, e.g., 'api' will match 'api-service', 'api-server', etc.) (optional)",
                        },
                    },
                    "required": [],
                },
            },
        }
