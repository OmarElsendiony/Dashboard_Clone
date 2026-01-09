import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool
import base64


class ResolveRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        auth_token: str,
        repository_name: Optional[str] = None,
        project_id: Optional[str] = None,
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

        repositories = data.get("repositories", {})
        repo_collaborators = data.get("repository_collaborators", {})

        # Get repository IDs the user has access to
        user_repo_ids = {
            rc["repository_id"]
            for rc in repo_collaborators.values()
            if rc["user_id"] == user_id
        }

        # Resolve a specific repository
        if repository_name:
            repository = next(
                (
                    r
                    for r in repositories.values()
                    if r["repository_id"] in user_repo_ids
                    and r["repository_name"] == repository_name
                    and (project_id is None or r.get("project_id") == project_id)
                ),
                None,
            )

            if not repository:
                return json.dumps(
                    {"success": False, "error": "Repository not found or access denied"}
                )
            # Remove owner id
            repo_copy = {**repository}
            repo_copy.pop("owner_id")
            repo_copy.pop("owner_type")
            return json.dumps({"success": True, "repository": repo_copy})

        # Otherwise, list all accessible repositories (optionally scoped by project)
        accessible_repositories = [
            r
            for r in repositories.values()
            if r["repository_id"] in user_repo_ids
            and (project_id is None or r.get("project_id") == project_id)
        ]
        copy_accessible_repositories = [{**repo} for repo in accessible_repositories]
        for i in copy_accessible_repositories:
            i.pop("owner_id")
            i.pop("owner_type")

        return json.dumps(
            {"success": True, "repositories": copy_accessible_repositories}
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_repository",
                "description": (
                    "Retrieves repository information that the authenticated user "
                    "has access to. The tool can resolve a specific repository by name, optionally "
                    "scoped to a project, or list all repositories accessible to the user. "
                    "Authentication is validated using the provided token, and only repositories "
                    "where the user is a collaborator are eligible for resolution."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token used to validate the requesting user. "
                                "The token must match a valid encoded token in the access token store."
                            ),
                        },
                        "repository_name": {
                            "type": "string",
                            "description": (
                                "Optional repository name to resolve. "
                                "If provided, the tool attempts to resolve a single repository "
                                "that matches this name and is accessible to the user."
                            ),
                        },
                        "project_id": {
                            "type": "string",
                            "description": (
                                "Optional project identifier used to scope the repository search. "
                                "If provided, only repositories belonging to this project are considered."
                            ),
                        },
                    },
                    "required": ["auth_token"],
                },
            },
        }
