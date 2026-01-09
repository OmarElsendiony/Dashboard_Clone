import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        owner_id: str,
        project_id: str,
        repository_name: str,
        visibility: str,
        default_branch: str,
        is_fork: bool,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """Create a new repository with branch and collaborator records."""
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        repositories_dict = data.get("repositories", {})
        repository_collaborators_dict = data.get("repository_collaborators", {})
        branches_dict = data.get("branches", {})
        users_dict = data.get("users", {})
        projects_dict = data.get("projects", {})

        owner_id_str = str(owner_id).strip()
        project_id_str = str(project_id).strip()
        repository_name_str = str(repository_name).strip()
        visibility_str = str(visibility).strip()
        default_branch_str = str(default_branch).strip()
        is_fork_bool = bool(is_fork)
        description_str = str(description).strip() if description else None
        user_id_str = str(user_id).strip() if user_id else None

        if owner_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"Owner with ID '{owner_id_str}' not found",
            })

        if project_id_str not in projects_dict:
            return json.dumps({
                "success": False,
                "error": f"Project with ID '{project_id_str}' not found",
            })

        if user_id_str and user_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id_str}' not found",
            })

        valid_visibilities = ["public", "private", "internal"]
        if visibility_str not in valid_visibilities:
            return json.dumps({
                "success": False,
                "error": f"Invalid visibility '{visibility_str}'. Must be one of: {', '.join(valid_visibilities)}",
            })

        # Check repository name uniqueness within the project
        for rid, repository in repositories_dict.items():
            if not isinstance(repository, dict):
                continue
            
            if str(repository.get("project_id")) == project_id_str and str(repository.get("repository_name", "")).strip() == repository_name_str:
                return json.dumps({
                    "success": False,
                    "error": f"Repository with name '{repository_name_str}' already exists in project '{project_id_str}' (repository_id: {rid})",
                })

        new_repo_id = generate_id(repositories_dict)
        new_repository = {
            "repository_id": new_repo_id,
            "project_id": project_id_str,
            "owner_id": owner_id_str,
            "repository_name": repository_name_str,
            "description": description_str,
            "visibility": visibility_str,
            "default_branch": default_branch_str,
            "is_fork": is_fork_bool,
            "created_at": timestamp,
            "updated_at": timestamp,
            "owner_type": "user",
            "is_archived": False,
            "is_template": False,
            "stars_count": 0,
            "forks_count": 0,
        }
        repositories_dict[new_repo_id] = new_repository

        new_branch_id = generate_id(branches_dict)
        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": new_repo_id,
            "branch_name": default_branch_str,
            "commit_sha": None,
            "created_at": timestamp,
            "is_default": True,
            "updated_at": timestamp
        }
        branches_dict[new_branch_id] = new_branch

        collaborators_created = []

        owner_collab_id = generate_id(repository_collaborators_dict)
        owner_collaborator = {
            "collaborator_id": owner_collab_id,
            "repository_id": new_repo_id,
            "user_id": owner_id_str,
            "permission_level": "admin",
            "added_at": timestamp,
            "status": "active"
        }
        repository_collaborators_dict[owner_collab_id] = owner_collaborator
        collaborators_created.append(owner_collaborator)

        if user_id_str and user_id_str != owner_id_str:
            user_collab_id = generate_id(repository_collaborators_dict)
            user_collaborator = {
                "collaborator_id": user_collab_id,
                "repository_id": new_repo_id,
                "user_id": user_id_str,
                "permission_level": "admin",
                "added_at": timestamp,
                "status": "active"
            }
            repository_collaborators_dict[user_collab_id] = user_collaborator
            collaborators_created.append(user_collaborator)

        return json.dumps({
            "success": True,
            "repository": new_repository,
            "default_branch": new_branch,
            "collaborators": collaborators_created,
            "message": f"Repository '{repository_name_str}' created successfully in project '{project_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the create_repository function."""
        return {
            "type": "function",
            "function": {
                "name": "create_repository",
                "description": (
                    "Create a new repository with default branch and collaborator records. "
                    "Validates that owner, project, and optional user exist. "
                    "Validates visibility is one of: public, private, internal. "
                    "Ensures repository_name is unique within the project. "
                    "Creates a branch record for the default branch with null commit_sha. "
                    "Creates a repository_collaborators record for owner_id with admin permission_level. "
                    "If user_id is provided and different from owner_id, creates an additional "
                    "repository_collaborators record for user_id with admin permission_level. "
                    "Returns the created repository, branch, and collaborator records."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner_id": {
                            "type": "string",
                            "description": "The ID of the user who owns the repository.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The ID of the project this repository belongs to.",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository. Must be unique within the project.",
                        },
                        "visibility": {
                            "type": "string",
                            "description": "The visibility of the repository (public/private/internal).",
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "The name of the default branch (e.g., 'main', 'master').",
                        },
                        "is_fork": {
                            "type": "boolean",
                            "description": "Whether this repository is a fork of another repository.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. The description of the repository.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Optional. Additional user to add as admin collaborator.",
                        },
                    },
                    "required": ["owner_id", "project_id", "repository_name", "visibility", "default_branch", "is_fork"],
                },
            },
        }