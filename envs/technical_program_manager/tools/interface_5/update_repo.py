import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateRepo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        repository_name: Optional[str] = None,
        description: Optional[str] = None,
        default_branch: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for repositories"}
            )

        if repository_id is None:
            return json.dumps({"success": False, "error": "repository_id is required"})

        repositories = data.get("repositories", {})

        repository = None
        repository_key_str = str(repository_id)

        if repository_key_str in repositories:
            repository_data = repositories[repository_key_str]
            if str(repository_data.get("repository_id")) == str(repository_id):
                repository = repository_data

        if not repository:
            for _repo_key, repository_data in repositories.items():
                if str(repository_data.get("repository_id")) == str(repository_id):
                    repository = repository_data
                    break

        if not repository:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with ID {str(repository_id)} not found",
                }
            )

        if project_id is not None:
            projects = data.get("projects", {})
            project = None
            project_key_str = str(project_id)

            if project_key_str in projects:
                project_data = projects[project_key_str]
                if str(project_data.get("project_id")) == str(project_id):
                    project = project_data

            if not project:
                for project_data in projects.values():
                    if str(project_data.get("project_id")) == str(project_id):
                        project = project_data
                        break

            if not project:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project with ID {str(project_id)} not found",
                    }
                )

        if (
            repository_name is None
            and description is None
            and default_branch is None
            and project_id is None
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field must be provided for update",
                }
            )

        if repository_name is not None:
            repository_name_str = str(repository_name)
            if len(repository_name_str) > 255:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository name exceeds maximum length of 255 characters (current length: {len(repository_name_str)})",
                    }
                )
            repository["repository_name"] = repository_name_str

        if description is not None:
            repository["description"] = str(description) if description else None

        if default_branch is not None:
            repository["default_branch"] = str(default_branch)

        if project_id is not None:
            repository["project_id"] = str(project_id)

        repository["updated_at"] = "2026-02-11T23:59:00"

        updated_repo = repository.copy()
        if updated_repo.get("repository_id") is not None:
            updated_repo["repository_id"] = str(updated_repo.get("repository_id"))
        if updated_repo.get("project_id") is not None:
            updated_repo["project_id"] = str(updated_repo.get("project_id"))
        if updated_repo.get("repository_name") is not None:
            updated_repo["repository_name"] = str(updated_repo.get("repository_name"))
        if updated_repo.get("description") is not None:
            updated_repo["description"] = str(updated_repo.get("description"))
        if updated_repo.get("default_branch") is not None:
            updated_repo["default_branch"] = str(updated_repo.get("default_branch"))
        if updated_repo.get("created_at") is not None:
            updated_repo["created_at"] = str(updated_repo.get("created_at"))
        if updated_repo.get("updated_at") is not None:
            updated_repo["updated_at"] = str(updated_repo.get("updated_at"))

        return json.dumps(
            {
                "success": True,
                "repository": updated_repo,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_repo",
                "description": "Update repository information. Can update repository name, description, default branch, or associated project. Use this to modify repository settings and configurations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The repository ID to update",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Optional new name for the repository",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional new description for the repository",
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "Optional new default branch name",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional new project ID to associate the repository with",
                        },
                    },
                    "required": ["repository_id"],
                },
            },
        }
