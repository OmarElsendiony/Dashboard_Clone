import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRepo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        repository_name: str,
        description: Optional[str] = None,
        default_branch: str = "main",
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for repositories"}
            )

        if project_id is None:
            return json.dumps({"success": False, "error": "project_id is required"})

        if not repository_name:
            return json.dumps(
                {"success": False, "error": "repository_name is required"}
            )

        repository_name_str = str(repository_name).strip()
        if len(repository_name_str) > 255:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository name exceeds maximum length of 255 characters (current length: {len(repository_name_str)})",
                }
            )
        if not repository_name_str:
            return json.dumps(
                {"success": False, "error": "repository_name is required"}
            )

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

        # Enforce unique repository_name (global uniqueness across repositories)
        repositories = data.get("repositories", {})
        incoming_name_norm = repository_name_str.lower()
        for _repo_key, repo_data in repositories.items():
            existing_name = repo_data.get("repository_name")
            if existing_name is None:
                continue
            if str(existing_name).strip().lower() == incoming_name_norm:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"repository_name '{repository_name_str}' already exists",
                    }
                )

        def generate_id(table: Dict[str, Any]) -> int:
            if not table:
                return 1
            return max(int(k) for k in table.keys()) + 1

        repositories = data.setdefault("repositories", {})
        repository_id = generate_id(repositories)
        timestamp = "2026-02-11T23:59:00"

        new_repository = {
            "repository_id": str(repository_id),
            "repository_name": repository_name_str,
            "description": str(description) if description is not None else None,
            "default_branch": str(default_branch),
            "project_id": str(project_id),
            "created_at": str(timestamp),
            "updated_at": str(timestamp),
        }

        repositories[str(repository_id)] = new_repository

        return json.dumps(
            {
                "success": True,
                "repository": new_repository,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_repo",
                "description": "Create a new repository for a project. repository_name must be unique across all repositories (global uniqueness). Use this to set up new code repositories with a name, description, and default branch configuration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The project ID where the repository will be created",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the repository",
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "The default branch name for the repository",
                            "default": "main",
                        },
                    },
                    "required": ["project_id", "repository_name"],
                },
            },
        }
