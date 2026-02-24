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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

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

        out_repos = []
        for repo in results:
            desc = repo.get("description")
            out_repos.append({
                "repository_id": str(repo.get("repository_id", "")),
                "repository_name": str(repo.get("repository_name", "")),
                "description": str(desc) if desc is not None else None,
                "default_branch": str(repo.get("default_branch", "main")),
                "created_at": str(repo.get("created_at", "")),
                "updated_at": str(repo.get("updated_at", "")),
            })

        return json.dumps({
            "success": bool(True),
            "repositories": out_repos,
            "count": int(len(out_repos)),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_repositories",
                "description": "Lists repositories, optionally filtered by name or identifier.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "Filter by repository name.",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository identifier.",
                        },
                    },
                    "required": [],
                },
            },
        }
