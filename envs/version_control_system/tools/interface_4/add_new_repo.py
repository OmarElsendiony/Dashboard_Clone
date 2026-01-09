import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddNewRepo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any], repository_name: str, auth_token: str, project_id: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        projects = data.get("projects", {})
        project_members = data.get("project_members", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        organizations = data.get("organizations", {})
        organization_members = data.get("organization_members", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # --- Authenticate requester ---
        encoded_token = encode(auth_token)
        token_info = next(
            (
                t
                for t in access_tokens.values()
                if t.get("token_encoded") == encoded_token
            ),
            None,
        )

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )

        requester_id = token_info["user_id"]

        # --- Validate project ---
        project = projects.get(project_id)
        if not project:
            return json.dumps({"success": False, "error": "Project not found"})

        # --- Authorization: Project Administrator ---
        is_project_admin = any(
            m
            for m in project_members.values()
            if m.get("project_id") == project_id
            and m.get("user_id") == requester_id
            and m.get("roles") == "Project Administrator"
        )

        if not is_project_admin:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Project Administrator role required",
                }
            )

        # --- Resolve ownership ---
        organization_id = project.get("organization_id")
        organization = organizations.get(organization_id)

        if not organization:
            return json.dumps(
                {"success": False, "error": "Owning organization not found"}
            )

        now = "2026-01-01T23:59:00"

        # --- Create repository record ---
        new_repository_id = str(
            max((int(k) for k in repositories.keys()), default=0) + 1
        )

        new_repository = {
            "repository_id": new_repository_id,
            "owner_type": "organization",
            "owner_id": organization_id,
            "project_id": project_id,
            "repository_name": repository_name,
            "description": "",
            "visibility": "private",
            "default_branch": None,
            "is_fork": False,
            "parent_repository_id": None,
            "is_archived": False,
            "is_template": False,
            "stars_count": 0,
            "forks_count": 0,
            "license_type": "unlicensed",
            "created_at": now,
            "updated_at": now,
            "pushed_at": None,
        }

        repositories[new_repository_id] = new_repository

        # --- Resolve organization owner ---
        organization_owner = next(
            (
                m
                for m in organization_members.values()
                if m.get("organization_id") == organization_id
                and m.get("role") == "owner"
            ),
            None,
        )

        def next_collaborator_id() -> str:
            return str(
                max((int(k) for k in repository_collaborators.keys()), default=0) + 1
            )

        # --- Grant requester admin access ---
        requester_collaborator_id = next_collaborator_id()
        requester_collaborator = {
            "collaborator_id": requester_collaborator_id,
            "repository_id": new_repository_id,
            "user_id": requester_id,
            "permission_level": "admin",
            "status": "active",
            "added_at": now,
        }

        repository_collaborators[requester_collaborator_id] = requester_collaborator

        # --- Grant organization owner admin access ---
        if organization_owner and organization_owner["user_id"] != requester_id:
            owner_collaborator_id = next_collaborator_id()
            repository_collaborators[owner_collaborator_id] = {
                "collaborator_id": owner_collaborator_id,
                "repository_id": new_repository_id,
                "user_id": organization_owner["user_id"],
                "permission_level": "admin",
                "status": "active",
                "added_at": now,
            }

        return json.dumps(
            {
                "success": True,
                "repository": new_repository,
                "admins": [
                    c
                    for c in repository_collaborators.values()
                    if c["repository_id"] == new_repository_id
                    and c["permission_level"] == "admin"
                ],
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_repo",
                "description": (
                    "Creates a repository under a project. The requesting user must be a "
                    "Project Administrator. The repository is owned by the project's "
                    "organization. Both the organization owner and the creator are granted "
                    "admin access automatically."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "Name of the repository.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project under which the repository is created.",
                        },
                    },
                    "required": ["repository_name", "auth_token", "project_id"],
                },
            },
        }
