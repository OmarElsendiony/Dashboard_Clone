import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchRepositories(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})

        results = []
        for repo in repositories.values():
            if repository_id is not None and str(repo.get("repository_id")) != str(
                repository_id
            ):
                continue

            if repository_name is not None:
                repository_name_lower = str(repository_name).strip().lower()
                db_name_lower = str(repo.get("repository_name") or "").lower()
                if db_name_lower != repository_name_lower:
                    continue

            results.append(repo)

        return json.dumps(
            {"success": True, "repositories": results, "count": len(results)}
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_repositories",
                "description": "List repositories, optionally filtered by name or identifier.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "Filter by repository name",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository identifier",
                        },
                    },
                    "required": [],
                },
            },
        }
