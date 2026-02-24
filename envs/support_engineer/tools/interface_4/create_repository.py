import json
import hashlib
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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        if repository_name is None:
            return json.dumps({
                "success": bool(False),
                "error": str("repository_name is required"),
            })
        repository_name = str(repository_name).strip()
        if not repository_name:
            return json.dumps({
                "success": bool(False),
                "error": str("repository_name is required"),
            })
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", repository_name):
            return json.dumps({
                "success": bool(False),
                "error": str("repository_name must not contain spaces or special characters; only letters, digits, underscores, and hyphens are allowed"),
            })

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})

        for repo in repositories.values():
            if repo.get("repository_name") == repository_name:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Repository with name '{repository_name}' already exists"),
                })

        if repositories:
            max_id = max(int(k) for k in repositories.keys())
            new_repository_id = str(max_id + 1)
        else:
            new_repository_id = str("1")

        static_timestamp = str("2026-02-02 23:59:00")

        new_repository = {
            "repository_id": str(new_repository_id),
            "repository_name": str(repository_name),
            "description": str(description) if description is not None else None,
            "default_branch": str(default_branch),
            "created_at": str(static_timestamp),
            "updated_at": str(static_timestamp),
        }

        repositories[new_repository_id] = new_repository

        if branches:
            max_branch_id = max(int(k) for k in branches.keys())
            new_branch_id = str(max_branch_id + 1)
        else:
            new_branch_id = str("1")

        commit_sha = hashlib.sha1(
            f"{new_repository_id}-{default_branch}-{new_branch_id}".encode()
        ).hexdigest()

        new_branch = {
            "branch_id": str(new_branch_id),
            "repository_id": str(new_repository_id),
            "branch_name": str(default_branch),
            "source_branch_name": None,
            "commit_sha": str(commit_sha),
            "linked_ticket_id": None,
            "created_by": None,
            "status": str("active"),
            "created_at": str(static_timestamp),
            "updated_at": str(static_timestamp),
        }

        branches[new_branch_id] = new_branch

        return json.dumps({
            "success": bool(True),
            "repository": new_repository,
            "branch": new_branch,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_repository",
                "description": "Creates a new repository with an optional description and default branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "Repository name; must be non-empty, no spaces or special characters (only letters, digits, underscores, hyphens).",
                        },
                        "description": {
                            "type": "string",
                            "description": "Repository description.",
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "Default branch name. Default: main.",
                        },
                    },
                    "required": ["repository_name"],
                },
            },
        }
