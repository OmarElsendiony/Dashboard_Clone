import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreatePipeline(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        workflow_name: str,
        yaml_path: str,
        repository_id: str,
        auth_token: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        files = data.get("files", {})
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

        # --- Authorization: write or admin ---
        permission = next(
            (
                c
                for c in repository_collaborators.values()
                if c.get("repository_id") == repository_id
                and c.get("user_id") == requester_id
                and c.get("permission_level") in {"write", "admin"}
            ),
            None,
        )

        if not permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Write or admin permission required.",
                }
            )

        # --- Enforce workflow uniqueness ---
        conflict = next(
            (
                w
                for w in workflows.values()
                if w.get("repository_id") == repository_id
                and (
                    w.get("workflow_name") == workflow_name
                    or w.get("workflow_path") == yaml_path
                )
                and w.get("status") != "deleted"
            ),
            None,
        )

        if conflict:
            return json.dumps(
                {
                    "success": False,
                    "error": "A workflow with the same name or path already exists in this repository.",
                }
            )
        # --- Validate yaml file exists in repository ---
        yaml_file = next(
            (
                f
                for f in files.values()
                if f.get("repository_id") == repository_id
                and f.get("file_path") == yaml_path
            ),
            None,
        )

        if not yaml_file:
            return json.dumps(
                {
                    "success": False,
                    "message": ("Workflow YAML file not found in repository. "),
                }
            )

        if not yaml_path.lower().endswith((".yml", ".yaml")):
            return json.dumps(
                {
                    "success": False,
                    "error": "Workflow file must be a .yml or .yaml file.",
                }
            )

        # --- Generate workflow ID ---
        try:
            workflow_id = str(max(int(k) for k in workflows.keys()) + 1)
        except ValueError:
            workflow_id = "1"

        now = "2026-01-01T23:59:00"

        # --- Create workflow ---
        workflow = {
            "workflow_id": workflow_id,
            "repository_id": repository_id,
            "workflow_name": workflow_name,
            "workflow_path": yaml_path,
            "trigger_event": "push",
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }

        workflows[workflow_id] = workflow

        return json.dumps({"success": True, "workflow": workflow})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_pipeline",
                "description": (
                    "Creates a new CI/CD workflow (pipeline) for a repository. "
                    "The requesting user must have write or admin permission. "
                    "The workflow is created in an active state and defaults to "
                    "triggering on push events."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workflow_name": {
                            "type": "string",
                            "description": "Human-readable name of the workflow.",
                        },
                        "yaml_path": {
                            "type": "string",
                            "description": "Path to the workflow YAML file in the repository.",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository where the workflow will be created.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                    },
                    "required": [
                        "workflow_name",
                        "yaml_path",
                        "repository_id",
                        "auth_token",
                    ],
                },
            },
        }
