import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
        description: Optional[str] = None,
        default_branch: str = "main",
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not repository_name or not str(repository_name).strip():
            return json.dumps(
                {"success": False, "error": "repository_name is required and must be a non-empty string"}
            )
        repository_name = str(repository_name).strip()
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", repository_name):
            return json.dumps(
                {
                    "success": False,
                    "error": "repository_name must not contain spaces or special characters; only letters, digits, underscores, and hyphens are allowed",
                }
            )

        repositories = data.get("repositories", {})

        for repo in repositories.values():
            if repo.get("repository_name") == repository_name:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with name '{repository_name}' already exists",
                    }
                )

        if repositories:
            max_id = max(int(k) for k in repositories.keys())
            new_repository_id = str(max_id + 1)
        else:
            new_repository_id = "1"

        static_timestamp = "2026-02-02 23:59:00"

        new_repository = {
            "repository_id": new_repository_id,
            "repository_name": repository_name,
            "description": description,
            "default_branch": default_branch,
            "created_at": static_timestamp,
            "updated_at": static_timestamp,
        }

        repositories[new_repository_id] = new_repository

        return json.dumps({"success": True, "repository": new_repository})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_repository",
                "description": "Create a new repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "Repository name; must be non-empty, no spaces or special characters (only letters, digits, underscores, hyphens)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Repository description",
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "Default branch name",
                        },
                    },
                    "required": ["repository_name"],
                },
            },
        }
