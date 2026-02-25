import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetRepositories(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        repository_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([repository_id, repository_name, project_id]):
            return json.dumps({
                "success": False,
                "error": "At least one filter parameter must be provided",
            })

        repository_id_str = str(repository_id).strip() if repository_id else None
        repository_name_str = str(repository_name).strip() if repository_name else None
        project_id_str = str(project_id).strip() if project_id else None

        repositories = data.get("repositories", {})
        pull_requests = data.get("pull_requests", {})
        projects = data.get("projects", {})

        if project_id_str is not None and project_id_str not in projects:
            return json.dumps({"success": False, "error": f"Project '{project_id_str}' not found"})

        results = []
        for repo in repositories.values():
            if repository_id_str is not None and str(repo.get("repository_id", "")) != repository_id_str:
                continue

            if repository_name_str is not None and repository_name_str.lower() != str(repo.get("repository_name", "")).lower():
                continue

            if project_id_str is not None and str(repo.get("project_id", "")) != project_id_str:
                continue

            repo_prs = []
            for pr in pull_requests.values():
                if str(pr.get("repository_id", "")) == str(repo.get("repository_id", "")):
                    repo_prs.append({
                        "pull_request_id": str(pr.get("pull_request_id", "")),
                        "title": str(pr.get("title", "")),
                        "state": str(pr.get("state", "")),
                    })
            repo_prs.sort(key=lambda x: int(x["pull_request_id"]))

            filtered_repo = {
                "repository_id": str(repo.get("repository_id", "")),
                "repository_name": str(repo.get("repository_name", "")),
                "description": str(repo.get("description", "")) if repo.get("description") else None,
                "project_id": str(repo.get("project_id", "")),
                "created_at": str(repo.get("created_at", "")),
                "updated_at": str(repo.get("updated_at", "")),
                "pull_requests": repo_prs,
            }
            results.append(filtered_repo)
        results.sort(key=lambda x: int(x["repository_id"]))
        return json.dumps({"success": True, "repositories": results, "count": int(len(results))})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_repositories",
                "description": "Retrieves repository records and associated pull requests based on optional filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by the exact unique repository identifier (repository_id).",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Filter by repository name (exact, case-insensitive).",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter by the project identifier (project_id).",
                        },
                    },
                    "anyOf": [
                        {"required": ["repository_id"]},
                        {"required": ["repository_name"]},
                        {"required": ["project_id"]},
                    ],
                    "required": [],
                },
            },
        }
