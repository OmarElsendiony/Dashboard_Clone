import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        repository_name: Optional[str] = None,
        description: Optional[str] = None,
        default_branch: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not repository_id:
            return json.dumps(
                {"success": False, "error": "repository_id is required to identify the repository"}
            )

        if not any([repository_name, description, default_branch]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field to update must be provided: repository_name, description, or default_branch",
                }
            )

        repositories = data.get("repositories", {})

        if str(repository_id) not in repositories:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with id '{repository_id}' not found",
                }
            )

        target_repo = repositories[str(repository_id)]

        if repository_name is not None:
            name = str(repository_name).strip()
            if not name:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Repository name must be a valid, non-empty string.",
                    }
                )
            if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Repository name must be a valid, non-empty string. It must not contain special characters or spaces. Underscores and hyphens can be used.",
                    }
                )
            repository_name = name
            for repo in repositories.values():
                if (
                    repo.get("repository_name") == repository_name
                    and str(repo.get("repository_id")) != str(repository_id)
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Repository with name '{repository_name}' already exists",
                        }
                    )
            target_repo["repository_name"] = repository_name
            target_repo["name"] = repository_name

        if description is not None:
            if description.strip() == "":
                return json.dumps(
                    {
                        "success": False,
                        "error": "description cannot be empty string",
                    }
                )
            target_repo["description"] = description

        if default_branch is not None:
            branches = data.get("branches", {})
            branch_exists = False
            for branch in branches.values():
                if (
                    str(branch.get("repository_id")) == str(repository_id)
                    and branch.get("branch_name") == default_branch
                ):
                    branch_exists = True
                    break

            if not branch_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Branch '{default_branch}' does not exist in repository '{repository_id}'",
                    }
                )
            target_repo["default_branch"] = default_branch

        static_timestamp = "2026-02-02 23:59:00"
        target_repo["updated_at"] = static_timestamp

        return json.dumps({"success": True, "repository": target_repo})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_repository",
                "description": "Update a repository's name, description, or default branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Required. Sole identifier of the repository to update",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Optional. New repository name; must be non-empty, no spaces or special characters (only letters, digits, underscores, hyphens)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. New repository description (field to update)",
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "Optional. New default branch name (field to update)",
                        },
                    },
                    "required": ["repository_id"],
                    "anyOf": [
                        {"required": ["repository_name"]},
                        {"required": ["description"]},
                        {"required": ["default_branch"]},
                    ],
                },
            },
        }
