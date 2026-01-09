import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
        project_id: str,
        user_id: str,
    ) -> str:
        """Retrieve repository information by repository_name and project_id, include collaborator details for user_id."""

        def find_repository(repositories_dict: Dict[str, Any], project_id_str: str, repository_name_str: str) -> Optional[Dict[str, Any]]:
            """Find repository by project_id and repository_name."""
            for rid, repository in repositories_dict.items():

                if str(repository.get("project_id")) == project_id_str and str(repository.get("repository_name", "")).strip() == repository_name_str:
                    repository_info = repository.copy()
                    repository_info["repository_id"] = str(rid)
                    return repository_info
            
            return None

        def find_collaborator_details(collaborators_dict: Dict[str, Any], repository_id: str, user_id_str: str) -> Optional[Dict[str, Any]]:
            """Find repository collaborator details for a specific user in a repository."""
            for collab_id, collaborator in collaborators_dict.items():

                if str(collaborator.get("repository_id")) == repository_id and str(collaborator.get("user_id")) == user_id_str:
                    collaborator_info = collaborator.copy()
                    collaborator_info["collaborator_id"] = str(collab_id)
                    return collaborator_info
            
            return None

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        repositories_dict = data.get("repositories", {})
        collaborators_dict = data.get("repository_collaborators", {})

        repository_name_str = str(repository_name).strip()
        project_id_str = str(project_id).strip()
        user_id_str = str(user_id).strip()

        repository = find_repository(repositories_dict, project_id_str, repository_name_str)

        if not repository:
            return json.dumps({
                "success": False,
                "error": f"Repository '{repository_name_str}' not found in project '{project_id_str}'"
            })

        collaborator_details = find_collaborator_details(
            collaborators_dict,
            repository["repository_id"],
            user_id_str
        )
        repository["collaborator_details"] = collaborator_details

        return json.dumps({
            "success": True,
            "repository": repository,
            "message": f"Repository '{repository_name_str}' found in project '{project_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the get_repository function."""
        return {
            "type": "function",
            "function": {
                "name": "get_repository",
                "description": (
                    "Retrieve repository information by repository_name and project_id. "
                    "Returns complete repository details including repository_id, owner_type, owner_id, "
                    "project_id, repository_name, description, visibility, default_branch, is_fork, "
                    "parent_repository_id, is_archived, is_template, stars_count, forks_count, "
                    "license_type, and timestamps. "
                    "Also includes repository collaborator details (permission_level, status) for the specified user_id. "
                    "The collaborator_details field will be null if the user is not a collaborator of that repository. "
                    "Returns an error if the repository is not found."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository to retrieve.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The ID of the project containing the repository.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user whose repository collaborator details to retrieve.",
                        },
                    },
                    "required": ["repository_name", "project_id", "user_id"],
                },
            },
        }