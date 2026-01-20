import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool
import base64


class AddProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_name: str,
        auth_token: str,
        organization_id: str,
        description: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        organizations = data.get("organizations", {})
        organization_members = data.get("organization_members", {})
        projects = data.get("projects", {})
        project_members = data.get("project_members", {})

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

        user_id = token_info.get("user_id")

        # --- Validate organization ---
        organization = organizations.get(organization_id)
        if not organization:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Organization with id {organization_id} not found",
                }
            )

        # --- Enforce organization membership ---
        is_member = any(
            m.get("user_id") == user_id and m.get("organization_id") == organization_id
            for m in organization_members.values()
        )

        if not is_member:
            return json.dumps(
                {
                    "success": False,
                    "error": "User is not a member of the specified organization",
                }
            )

        # --- Prevent duplicate project names within organization ---
        duplicate_project = next(
            (
                p
                for p in projects.values()
                if p.get("organization_id") == organization_id
                and p.get("project_name") == project_name
            ),
            None,
        )

        if duplicate_project:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project '{project_name}' already exists in this organization",
                }
            )

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        timestamp = "2026-01-01T23:59:00"

        # --- Create project ---
        project_id = generate_id(projects)
        project = {
            "project_id": project_id,
            "project_name": project_name,
            "organization_id": organization_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            "workspace_id": None,
            "project_key": None,
            "status": "active",
            "description": description or "",
            "is_private": True,
        }
        projects[project_id] = project

        # --- Add creator as project member ---
        project_member_id = generate_id(project_members)
        project_members[project_member_id] = {
            "project_member_id": project_member_id,
            "project_id": project_id,
            "user_id": user_id,
            "roles": "Project Administrator",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        return json.dumps({"success": True, "project": project})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_project",
                "description": (
                    "Creates a new project within an organization. "
                    "The requesting user must be a member of the specified organization. "
                    "Project names must be unique within the organization. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "The name of the project to be created.",
                        },
                        "organization_id": {
                            "type": "string",
                            "description": (
                                "The identifier of the organization under which "
                                "the project will be created."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token used to validate the requesting user."
                            ),
                        },
                        "description": {
                            "type": "string",
                            "description": (
                                "A detailed information about the project."
                            ),
                        },
                    },
                    "required": ["project_name", "organization_id", "auth_token"],
                },
            },
        }
