import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import base64


class ResolvePullRequest(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], pull_request_number: int, auth_token: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        access_tokens = data.get("access_tokens", {})

        def encode(text):
            """
            Encodes text into Base64 format.
            1. Converts string to bytes (.encode).
            2. Encodes bytes to Base64 bytes.
            3. Converts back to string (.decode) for readable output.
            """
            text_bytes = text.encode("utf-8")
            encoded_bytes = base64.b64encode(text_bytes)
            return encoded_bytes.decode("utf-8")

        encoded_token = encode(auth_token)
        # validate auth token
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
        pull_requests = data.get("pull_requests", {})

        if not pull_request_number:
            return json.dumps(
                {"success": False, "error": "pull_request_number is required"}
            )

        pull_request = next(
            (
                pr
                for pr in pull_requests.values()
                if pr.get("pull_request_number") == pull_request_number
            ),
            None,
        )

        if not pull_request:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Pull request with number {pull_request_number} not found",
                }
            )

        return json.dumps({"success": True, "pull_request": pull_request})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_pull_request",
                "description": (
                    "Resolves and retrieves a pull request by its pull request number. "
                    "The tool performs a direct lookup and returns the matching pull request "
                    "if it exists. This is a read-only resolver and does not enforce "
                    "authentication or authorization checks."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_number": {
                            "type": "integer",
                            "description": (
                                "The unique pull request number used to identify the pull request. "
                                "This value must match the pull request number exactly."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token used to validate the requesting user. "
                                "The token must correspond to a valid encoded token in the access token store."
                            ),
                        },
                    },
                    "required": ["pull_request_number", "auth_token"],
                },
            },
        }
