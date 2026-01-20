import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import base64


class ResolvePullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_number: int,
        repository_id: str,
        auth_token: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repo_collaborators = data.get("repository_collaborators", {})
        pull_requests = data.get("pull_requests", {})

        def encode(text: str) -> str:
            text_bytes = text.encode("utf-8")
            encoded_bytes = base64.b64encode(text_bytes)
            return encoded_bytes.decode("utf-8")

        # --- Authenticate user ---
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
        target_repo = repositories.get(repository_id)
        if not target_repo:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with id {repository_id} not found",
                }
            )

        # --- Check repository permissions ---
        collaborator = next(
            (
                collab
                for collab in repo_collaborators.values()
                if collab.get("repository_id") == repository_id
                and collab.get("user_id") == requester_id
            ),
            None,
        )

        if not collaborator:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied: user has no permissions on this repository",
                }
            )

        # --- Validate pull request number ---
        if not pull_request_number:
            return json.dumps(
                {"success": False, "error": "pull_request_number is required"}
            )

        # --- Retrieve pull request ---
        pull_request = next(
            (
                pr
                for pr in pull_requests.values()
                if pr.get("pull_request_number") == pull_request_number
                and pr.get("repository_id") == repository_id
            ),
            None,
        )

        if not pull_request:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Pull request {pull_request_number} not found "
                        f"in repository {repository_id}"
                    ),
                }
            )

        return json.dumps(
            {
                "success": True,
                "pull_request": pull_request,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_pull_request",
                "description": (
                    "Retrieves a pull request by its pull request number "
                    "after validating repository access permissions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_number": {
                            "type": "integer",
                            "description": (
                                "The unique pull request number used to identify the pull request."
                            ),
                        },
                        "repository_id": {
                            "type": "string",
                            "description": (
                                "The repository ID where the pull request exists."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token used to validate the requesting user."
                            ),
                        },
                    },
                    "required": [
                        "pull_request_number",
                        "repository_id",
                        "auth_token",
                    ],
                },
            },
        }
