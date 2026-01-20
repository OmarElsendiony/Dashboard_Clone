import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool
import base64


class ResolveBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        auth_token: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})

        def encode(text: str) -> str:
            text_bytes = text.encode("utf-8")
            encoded_bytes = base64.b64encode(text_bytes)
            return encoded_bytes.decode("utf-8")

        encoded_token = encode(auth_token)

        # Validate auth token
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

        user_id = token_info.get("user_id")

        branches = data.get("branches", {})
        repo_collaborators = data.get("repository_collaborators", {})

        # Check repository access
        has_access = any(
            rc["user_id"] == user_id and rc["repository_id"] == repository_id
            for rc in repo_collaborators.values()
        )

        if not has_access:
            return json.dumps(
                {"success": False, "error": "Access denied to repository"}
            )

        # Get branches for repository
        repo_branches = [
            b for b in branches.values() if b.get("repository_id") == repository_id
        ]

        if not repo_branches:
            return json.dumps(
                {"success": False, "error": "No branches found for repository"}
            )

        # Apply optional filters
        if filters:
            if "branch_name" in filters:
                repo_branches = [
                    b
                    for b in repo_branches
                    if b.get("branch_name") == filters["branch_name"]
                ]

            if "is_default" in filters:
                repo_branches = [
                    b
                    for b in repo_branches
                    if b.get("is_default") == filters["is_default"]
                ]

        return json.dumps({"success": True, "branches": repo_branches})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_branch",
                "description": (
                    "Resolves and retrieves branches belonging to a specific repository that the "
                    "authenticated user has access to."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the repository whose branches are to be resolved. "
                                "The user must have collaborator access to this repository."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token used to validate the requesting user. "
                                "The token must correspond to a valid encoded token in the access token store."
                            ),
                        },
                        "filters": {
                            "type": "object",
                            "description": (
                                "Optional filtering criteria applied to the branch resolution. "
                                "Supported filters include 'branch_name' (exact match) and "
                                "'is_default' (boolean)."
                            ),
                            "additionalProperties": True,
                        },
                    },
                    "required": ["repository_id", "auth_token"],
                },
            },
        }
