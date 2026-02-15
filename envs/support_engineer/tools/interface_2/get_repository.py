import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        repos_dict = data.get("repositories", {})
        search_name = str(repository_name).strip().lower() if repository_name else ""

        if search_name:
            target_repo = None
            target_repo_id = None

            for r_id, r_data in repos_dict.items():
                r_name = str(r_data.get("repository_name", "")).strip().lower()
                if r_name == search_name:
                    target_repo = r_data
                    target_repo_id = r_id
                    break
                alt_name = str(r_data.get("name", "")).strip().lower()
                if alt_name == search_name:
                    target_repo = r_data
                    target_repo_id = r_id
                    break

            if not target_repo:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with name '{repository_name}' not found",
                    }
                )

            response = {
                "repository_id": str(target_repo_id),
                "repository_name": str(target_repo.get("repository_name", "")),
                "name": (
                    str(target_repo.get("name", ""))
                    if target_repo.get("name")
                    else None
                ),
                "description": (
                    str(target_repo.get("description", ""))
                    if target_repo.get("description")
                    else None
                ),
                "default_branch": str(target_repo.get("default_branch", "main")),
                "created_at": str(target_repo.get("created_at", None)),
                "updated_at": str(target_repo.get("updated_at", None)),
            }
            return json.dumps({"success": True, "repository": response})
        else:
            response = repos_dict
            return json.dumps({"success": True, "repositories": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_repository",
                "description": (
                    "Retrieves repository details including default branch information. "
                    "This function identifies the correct codebase for incident investigation and engineering fixes. "
                    "Use this after incident brief construction to locate service repositories, "
                    "before creating fix branches to verify repository existence, "
                    "when analyzing codebases for root cause identification, "
                    "or prior to pull request operations to confirm target repository."
                    "A repository represents a service in the system. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository to retrieve",
                        }
                    },
                    "required": [],
                },
            },
        }
