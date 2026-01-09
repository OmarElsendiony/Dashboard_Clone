import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetRunPipeline(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        workflow_name: str,
        auth_token: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        workflows = data.get("workflows", {})

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

        # --- Authorization: read / write / admin ---
        permission = next(
            (
                c
                for c in repository_collaborators.values()
                if c.get("repository_id") == repository_id
                and c.get("user_id") == requester_id
                and c.get("permission_level") in {"read", "write", "admin"}
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

        # --- Resolve workflow ---
        workflow = next(
            (
                w
                for w in workflows.values()
                if w.get("repository_id") == repository_id
                and w.get("workflow_name") == workflow_name
                and w.get("status") != "deleted"
            ),
            None,
        )

        if not workflow:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Workflow '{workflow_name}' not found in repository",
                }
            )

        return json.dumps({"success": True, "workflow": workflow})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_run_pipeline",
                "description": (
                    "Retrieves a workflow (pipeline) configuration by name for a repository. "
                    "The user must have at least read access to the repository."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The repository containing the workflow.",
                        },
                        "workflow_name": {
                            "type": "string",
                            "description": "The name of the workflow to retrieve.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                    },
                    "required": ["repository_id", "workflow_name", "auth_token"],
                },
            },
        }
