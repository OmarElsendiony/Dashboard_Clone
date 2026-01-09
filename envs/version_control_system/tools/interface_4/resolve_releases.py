import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ResolveReleases(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], repository_id: str, auth_token: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        if not repository_id:
            return json.dumps(
                {"success": False, "message": f"repository_id is required."}
            )
        if not auth_token:
            return json.dumps(
                {
                    "success": False,
                    "message": f"auth_token is required for authentication.",
                }
            )

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        releases = data.get("releases", {})

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

        # --- Authorization: admin ---
        permission = next(
            (
                c
                for c in repository_collaborators.values()
                if c.get("repository_id") == repository_id
                and c.get("user_id") == requester_id
                and c.get("permission_level") in {"admin", "write"}
            ),
            None,
        )

        if not permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Repository access required.",
                }
            )

        # --- Resolve releases ---
        resolved_releases = [
            r for r in releases.values() if r.get("repository_id") == repository_id
        ]

        resolved_releases.sort(key=lambda r: r.get("created_at", ""))

        return json.dumps(
            {
                "success": True,
                "repository_id": repository_id,
                "count": len(resolved_releases),
                "releases": resolved_releases,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_releases",
                "description": (
                    "Retrieves all releases for a repository. "
                    "The requesting user must have at least write access "
                    "to the repository."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The repository whose releases should be resolved.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                    },
                    "required": ["repository_id", "auth_token"],
                },
            },
        }
