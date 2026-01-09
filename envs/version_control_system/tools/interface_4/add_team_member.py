import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddTeamMember(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        auth_token: str,
        permission_config: Dict[str, Any],
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([organization_id, project_id, repository_id]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one scope (organization, project, repository) must be specified",
                }
            )

        # Tables
        access_tokens = data.get("access_tokens", {})
        organization_members = data.get("organization_members", {})
        project_members = data.get("project_members", {})
        repository_members = data.get("repository_collaborators", {})
        organizations = data.get("organizations", {})
        projects = data.get("projects", {})
        repositories = data.get("repositories", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        def generate_id(table: dict) -> str:
            return str(max((int(k) for k in table.keys()), default=0) + 1)

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
        now = "2026-01-01T23:59:00"
        result = {}

        # ================= ORGANIZATION =================
        if organization_id:
            org_role = permission_config.get("organization_role")
            if not org_role:
                return json.dumps(
                    {"success": False, "error": "organization_role is required"}
                )

            if org_role not in {"owner", "member"}:
                return json.dumps(
                    {"success": False, "error": "Invalid organization_role"}
                )

            if organization_id not in organizations:
                return json.dumps({"success": False, "error": "Organization not found"})

            requester_is_owner = any(
                m
                for m in organization_members.values()
                if m["organization_id"] == organization_id
                and m["user_id"] == requester_id
                and m["role"] == "owner"
            )
            if not requester_is_owner:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Organization owner permission required",
                    }
                )

            existing = next(
                (
                    m
                    for m in organization_members.values()
                    if m["organization_id"] == organization_id
                    and m["user_id"] == user_id
                ),
                None,
            )

            if existing:
                existing["role"] = org_role
                result["organization_member_updated"] = existing
            else:
                member_id = generate_id(organization_members)
                new_member = {
                    "membership_id": member_id,
                    "organization_id": organization_id,
                    "user_id": user_id,
                    "role": org_role,
                    "joined_at": now,
                    "status": "active",
                }
                organization_members[member_id] = new_member
                result["organization_member_created"] = new_member

        # ================= PROJECT =================
        if project_id:
            proj_role = permission_config.get("project_role")
            if not proj_role:
                return json.dumps(
                    {"success": False, "error": "project_role is required"}
                )

            valid_roles = {
                "Build_Administrator",
                "Contributor",
                "Project Administrator",
                "Reader",
                "Release_Administrator",
            }
            if proj_role not in valid_roles:
                return json.dumps({"success": False, "error": "Invalid project_role"})

            project = projects.get(project_id)
            if not project:
                return json.dumps({"success": False, "error": "Project not found"})

            requester_is_admin = any(
                m
                for m in project_members.values()
                if m["project_id"] == project_id
                and m["user_id"] == requester_id
                and m["roles"] == "Project Administrator"
            )
            if not requester_is_admin:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Project Administrator permission required",
                    }
                )

            # Target must belong to parent org
            if not any(
                m
                for m in organization_members.values()
                if m["organization_id"] == project["organization_id"]
                and m["user_id"] == user_id
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Target user is not a member of the parent organization",
                    }
                )

            existing = next(
                (
                    m
                    for m in project_members.values()
                    if m["project_id"] == project_id and m["user_id"] == user_id
                ),
                None,
            )

            if existing:
                existing["roles"] = proj_role
                existing["updated_at"] = now
                result["project_member_updated"] = existing
            else:
                member_id = generate_id(project_members)
                new_member = {
                    "project_member_id": member_id,
                    "project_id": project_id,
                    "user_id": user_id,
                    "roles": proj_role,
                    "created_at": now,
                    "updated_at": now,
                }
                project_members[member_id] = new_member
                result["project_member_created"] = new_member

        # ================= REPOSITORY =================
        if repository_id:
            repo_perm = permission_config.get("repository_permission")
            if not repo_perm:
                return json.dumps(
                    {"success": False, "error": "repository_permission is required"}
                )

            if repo_perm not in {"read", "write", "admin"}:
                return json.dumps(
                    {"success": False, "error": "Invalid repository_permission"}
                )

            repo = repositories.get(repository_id)
            if not repo:
                return json.dumps({"success": False, "error": "Repository not found"})

            requester_is_admin = any(
                m
                for m in repository_members.values()
                if m["repository_id"] == repository_id
                and m["user_id"] == requester_id
                and m["permission_level"] == "admin"
            )
            if not requester_is_admin:
                return json.dumps(
                    {"success": False, "error": "Repository admin permission required"}
                )

            # Target must belong to parent project
            if not any(
                m
                for m in project_members.values()
                if m["project_id"] == repo["project_id"] and m["user_id"] == user_id
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Target user is not a member of the parent project",
                    }
                )

            existing = next(
                (
                    m
                    for m in repository_members.values()
                    if m["repository_id"] == repository_id and m["user_id"] == user_id
                ),
                None,
            )

            if existing:
                existing["permission_level"] = repo_perm
                result["repository_member_updated"] = existing
            else:
                member_id = generate_id(repository_members)
                new_member = {
                    "collaborator_id": member_id,
                    "repository_id": repository_id,
                    "user_id": user_id,
                    "permission_level": repo_perm,
                    "status": "active",
                    "added_at": now,
                }
                repository_members[member_id] = new_member
                result["repository_member_created"] = new_member

        if not result:
            return json.dumps(
                {"success": False, "error": "No updates or additions performed"}
            )

        return json.dumps({"success": True, **result})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_team_member",
                "description": (
                    "Adds a user to one or more scopes (organization, project, repository) in one run. "
                    "Validates requester permissions and parent memberships. Returns the newly created memberships."
                    "permission_config includes Options[('organization_role', ['owner', 'member']), ('project_role', ['Build_Administrator', 'Contributor', 'Project Administrator', 'Reader', 'Release_Administrator']), ('repository_permission', ['admin', 'write', 'read'])]"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "ID of the user to add.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requester.",
                        },
                        "organization_id": {
                            "type": "string",
                            "description": "Optional organization ID (owner role required).",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID (Project Administrator role required).",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Optional repository ID (admin permission required).",
                        },
                        "permission_config": {
                            "type": "object",
                            "description": "The role and permissions to apply per scope.",
                        },
                    },
                    "required": ["user_id", "auth_token", "permission_config"],
                },
            },
        }
