import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ModifyProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any], project_id: str, auth_token: str, updates: Dict[str, Any]
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not isinstance(updates, dict):
            return json.dumps(
                {"success": False, "error": "Updates must be a dictionary"}
            )

        access_tokens = data.get("access_tokens", {})
        projects = data.get("projects", {})
        project_members = data.get("project_members", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

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

        user_id = token_info.get("user_id")

        # --- Validate project ---
        project = projects.get(project_id)
        if not project:
            return json.dumps(
                {"success": False, "error": f"Project with id {project_id} not found"}
            )

        # --- Validate project membership ---
        is_member = any(
            m
            for m in project_members.values()
            if m.get("user_id") == user_id and m.get("project_id") == project_id
        )

        if not is_member:
            return json.dumps(
                {
                    "success": False,
                    "error": "User access restricted. User is not a member of this project",
                }
            )

        # --- Allowed fields for update ---
        allowed_fields = {"project_name", "description"}

        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid update fields: {', '.join(invalid_fields)}",
                }
            )

        # --- Apply updates ---
        for key, value in updates.items():
            project[key] = value

        return json.dumps({"success": True, "project": {"project": project}})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_project",
                "description": (
                    "Updates mutable fields of an existing project. Allowed fields include 'project_name' and 'description'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project to be updated.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                        "updates": {
                            "type": "object",
                            "description": (
                                "A dictionary of project fields to update. "
                                "Only allowed mutable fields are accepted."
                            ),
                        },
                    },
                    "required": ["project_id", "auth_token", "updates"],
                },
            },
        }
