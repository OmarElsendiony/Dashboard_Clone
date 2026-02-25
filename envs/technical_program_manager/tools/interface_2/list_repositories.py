import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class ListRepositories(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not project_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'project_id'"
            })

        repositories_dict = data.get("repositories", {})

        if not isinstance(repositories_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'repositories' must be a dict"
            })

        project_id_clean = str(project_id).strip()

        repository_list = []

        for repo_id, repo_data in repositories_dict.items():

            if str(repo_data.get("project_id", "")).strip() != project_id_clean:
                continue

            repository_list.append({
                "repository_id": str(repo_id),
                "repository_name": str(repo_data.get("repository_name", "")),
                "description": str(repo_data.get("description", "")),
                "default_branch": str(repo_data.get("default_branch", "")),
                "project_id": str(repo_data.get("project_id", "")),
                "created_at": str(repo_data.get("created_at", "")),
                "updated_at": str(repo_data.get("updated_at", ""))
            })

        return json.dumps({
            "success": True,
            "repositories": repository_list
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_repositories",
                "description": "Lists all repositories associated with a specific project. "
                               "This function retrieves repository metadata within the project context "
                               "before reviewing pull requests, validating merge activity, or tracking code changes in TPM workflows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project whose repositories are to be listed."
                        }
                    },
                    "required": ["project_id"]
                }
            }
        }
