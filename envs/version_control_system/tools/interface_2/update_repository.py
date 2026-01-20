import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool


class UpdateRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        repository_name: Optional[str] = None,
        project_id: Optional[str] = None,
        is_fork: Optional[bool] = None,
        description: Optional[str] = None,
        default_branch: Optional[str] = None,
    ) -> str:
        timestamp = "2026-01-01T23:59:00"

        def check_repository_name_uniqueness(
            repositories_dict: Dict[str, Any],
            repository_name_str: str,
            project_id_str: str,
            repository_id_str: str,
        ) -> Tuple[bool, Optional[str]]:
            """Check if repository name is unique within project, excluding current repository."""
            for rid, repo in repositories_dict.items():
                if str(rid) == repository_id_str:
                    continue

                if (str(repo.get("project_id")) == project_id_str and 
                    str(repo.get("repository_name", "")).strip() == repository_name_str):
                    return (
                        False,
                        f"Repository with name '{repository_name_str}' already exists in project '{project_id_str}' (repository_id: {rid})",
                    )

            return True, None

        def validate_and_update_default_branch(
            branches_dict: Dict[str, Any],
            repository_id_str: str,
            default_branch_str: str,
        ) -> Tuple[bool, Optional[str]]:
            """Validate default branch exists and update is_default flags."""
            branch_found = False
            
            # Check if the new default branch exists
            for _, branch in branches_dict.items():
                if not isinstance(branch, dict):
                    continue
                
                if (str(branch.get("repository_id")) == repository_id_str and 
                    str(branch.get("branch_name", "")).strip() == default_branch_str):
                    branch_found = True
                    break
            
            if not branch_found:
                return False, f"Branch '{default_branch_str}' not found in repository '{repository_id_str}'"
            
            # Update is_default flags
            for _, branch in branches_dict.items():
                if not isinstance(branch, dict):
                    continue
                
                if str(branch.get("repository_id")) == repository_id_str:
                    if str(branch.get("branch_name", "")).strip() == default_branch_str:
                        branch["is_default"] = True
                    else:
                        branch["is_default"] = False
            
            return True, None

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Check at least one update parameter is provided
        if not any([repository_name, project_id, is_fork is not None, description, default_branch]):
            return json.dumps({
                "success": False,
                "error": "At least one of repository_name, project_id, is_fork, description, or default_branch must be provided for update",
            })

        # Get data containers
        repositories_dict = data.get("repositories", {})
        projects_dict = data.get("projects", {})
        branches_dict = data.get("branches", {})

        # Convert to strings
        repository_id_str = str(repository_id).strip()
        repository_name_str = str(repository_name).strip() if repository_name else None
        project_id_str = str(project_id).strip() if project_id else None
        default_branch_str = str(default_branch).strip() if default_branch else None

        # Check if repository exists
        if repository_id_str not in repositories_dict:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id_str}' not found",
            })

        repository = repositories_dict[repository_id_str]
        current_project_id = str(repository.get("project_id"))

        # Determine which project_id to use for uniqueness check
        target_project_id = project_id_str if project_id_str else current_project_id

        # Validate new project exists if provided
        if project_id_str and project_id_str not in projects_dict:
            return json.dumps({
                "success": False,
                "error": f"Project with ID '{project_id_str}' not found",
            })

        # Check repository name uniqueness if name is changing OR project is changing
        if repository_name_str or project_id_str:
            name_to_check = repository_name_str if repository_name_str else str(repository.get("repository_name", "")).strip()
            is_valid, error_msg = check_repository_name_uniqueness(
                repositories_dict, name_to_check, target_project_id, repository_id_str
            )
            if not is_valid:
                return json.dumps({"success": False, "error": error_msg})

        # Validate and update default branch if provided
        if default_branch_str:
            is_valid, error_msg = validate_and_update_default_branch(
                branches_dict, repository_id_str, default_branch_str
            )
            if not is_valid:
                return json.dumps({"success": False, "error": error_msg})
            
            repository["default_branch"] = default_branch_str

        if repository_name_str:
            repository["repository_name"] = repository_name_str

        if project_id_str:
            repository["project_id"] = project_id_str

        if is_fork is not None:
            repository["is_fork"] = bool(is_fork)

        if description is not None:
            repository["description"] = str(description).strip()

        repository["updated_at"] = timestamp

        repository_return = repository.copy()
        repository_return["repository_id"] = repository_id_str

        return json.dumps({
            "success": True,
            "repository": repository_return,
            "message": f"Repository '{repository.get('repository_name')}' updated successfully",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_repository",
                "description": "Updates repository information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository to update.",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "The new name for the repository. Must be unique within the project (optional).",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The new project ID to move the repository to (optional).",
                        },
                        "is_fork": {
                            "type": "boolean",
                            "description": "Whether the repository is a fork (optional).",
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description for the repository (optional).",
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "The new default branch name. Must exist in the repository (optional).",
                        },
                    },
                    "required": ["repository_id"],
                },
            },
        }
