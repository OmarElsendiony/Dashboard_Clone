import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateWorkItem(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        title: str,
        auth_token: str,
        description: Optional[str] = None,
        priority: Optional[str] = "low",
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        issues = data.get("issues", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # --- Authenticate requester ---
        encoded_token = encode(auth_token)
        token_info = next(
            (
                info
                for info in access_tokens.values()
                if info.get("token_encoded") == encoded_token
            ),
            None,
        )

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )

        requester_id = token_info.get("user_id")

        # --- Validate repository ---
        repository = repositories.get(repository_id)
        if not repository:
            return json.dumps({"success": False, "error": "Repository not found"})

        # --- Authorization: write or admin ---
        requester_permission = next(
            (
                c
                for c in repository_collaborators.values()
                if c.get("repository_id") == repository_id
                and c.get("user_id") == requester_id
                and c.get("permission_level") in {"write", "admin"}
            ),
            None,
        )

        if not requester_permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Write or admin permission required.",
                }
            )

        # --- Generate issue_id ---
        try:
            new_issue_id = str(max(int(k) for k in issues.keys()) + 1)
        except ValueError:
            new_issue_id = "1"

        # --- Generate issue_number (per repository) ---
        repo_issue_numbers = [
            i.get("issue_number", 0)
            for i in issues.values()
            if i.get("repository_id") == repository_id
        ]
        next_issue_number = max(repo_issue_numbers, default=0) + 10

        now = "2026-01-01T23:59:00"
        if priority not in {"low", "medium", "high", "critical"}:
            return json.dumps(
                {
                    "success": False,
                    "message": 'Invalid priority level. Accepted priorities ("low", "medium", "high", "critical")',
                }
            )
        # --- Create issue record ---
        issue_entry = {
            "issue_id": new_issue_id,
            "repository_id": repository_id,
            "issue_number": next_issue_number,
            "title": title + " " + str(next_issue_number),
            "description": description,
            "author_id": requester_id,
            "assignee_id": None,
            "status": "open",
            "priority": priority,
            "issue_type": "feature",
            "closed_at": None,
            "created_at": now,
            "updated_at": now,
        }

        issues[new_issue_id] = issue_entry

        # --- Output with work_item_id alias ---
        output_item = {**issue_entry, "work_item_id": issue_entry["issue_id"]}

        return json.dumps({"success": True, "work_item": output_item})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_work_item",
                "description": (
                    "Creates a new work item (issue) within a repository. "
                    "The user must have at least write or admin level permission on the target repository. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": (
                                "Unique identifier of the repository where the work item will be created. "
                            ),
                        },
                        "title": {
                            "type": "string",
                            "description": (
                                "Short, descriptive title of the work item. "
                            ),
                        },
                        "description": {
                            "type": "string",
                            "description": (
                                "Optional detailed description of the work item, "
                                "providing context, requirements, or reproduction steps."
                            ),
                        },
                        "priority": {
                            "type": "string",
                            "description": (
                                "Priority level of the work item. "
                                "Accepted values are: 'low', 'medium', 'high', 'critical'. "
                                "Defaults to 'low' if not explicitly provided."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token used to identify the user and validate repository permissions."
                            ),
                        },
                    },
                    "required": ["repository_id", "title", "auth_token"],
                },
            },
        }
