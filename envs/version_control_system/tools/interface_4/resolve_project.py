import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool
import base64


class ResolveProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        auth_token: str,
        project_name: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        access_tokens = data.get("access_tokens", {})

        def encode(text):
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

        user_id = token_info.get("user_id")

        project_memberships = data.get("project_members", {})
        user_project_ids = {
            pm["project_id"]
            for pm in project_memberships.values()
            if pm["user_id"] == user_id
        }

        projects_data = data.get("projects", {})

        if project_name and organization_id:
            project = next(
                (
                    p
                    for p in projects_data.values()
                    if p["project_id"] in user_project_ids
                    and p["project_name"] == project_name
                    and p["organization_id"] == organization_id
                ),
                None,
            )
        elif project_name:
            project = next(
                (
                    p
                    for p in projects_data.values()
                    if p["project_id"] in user_project_ids
                    and p["project_name"] == project_name
                ),
                None,
            )
        elif organization_id:
            projects = [
                p
                for p in projects_data.values()
                if p["project_id"] in user_project_ids
                and p["organization_id"] == organization_id
            ]
            return json.dumps({"success": True, "projects": projects})
        else:
            accessible_projects = [
                p for p in projects_data.values() if p["project_id"] in user_project_ids
            ]
            return json.dumps({"success": True, "projects": accessible_projects})

        if not project:
            return json.dumps(
                {"success": False, "error": "Project not found or access denied"}
            )

        return json.dumps({"success": True, "project": project})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_project",
                "description": (
                    "Retrieves project(s) by name that the requesting user is a member of. "
                    "Can optionally filter results to a specific organization. "
                    "Returns all accessible projects if no filters are provided."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": (
                                "The name of the project to resolve. "
                                "This must match the project name exactly."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token used to validate the requesting user. "
                                "The token must correspond to a valid encoded token in the access token store."
                            ),
                        },
                        "organization_id": {
                            "type": "string",
                            "description": (
                                "Optional organization identifier used to scope the project search. "
                                "If provided, the resolved project must belong to this organization."
                            ),
                        },
                    },
                    "required": ["auth_token"],
                },
            },
        }
