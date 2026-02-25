import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool


class RemoveUsersFromProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_identifiers: List[Dict[str, str]],
        project_identifier: Dict[str, str],
    ) -> str:
        # 1. Basic data integrity check
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not isinstance(user_identifiers, list):
            return json.dumps(
                {
                    "success": False,
                    "error": "user_identifiers must be a list.",
                }
            )

        if not isinstance(project_identifier, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "project_identifier must be a dictionary object.",
                }
            )

        now = "2026-02-11T23:59:00"
        users = data.get("users", {})
        projects = data.get("projects", {})
        members = data.get("project_members", {})
        work_items = data.get("work_items", {})

        # Validate each user_identifier in the list
        for u_ident in user_identifiers:
            if not isinstance(u_ident, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Each item in user_identifiers must be a dictionary object.",
                    }
                )
            # Validate exactly one key provided for each user identifier
            user_keys = [k for k in ["user_id", "username", "email"] if u_ident.get(k)]
            if len(user_keys) != 1:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Exactly one identifier key required for each user_identifier (user_id, username, or email).",
                    }
                )

        # Validate exactly one key provided for project_identifier
        project_keys = [
            k
            for k in ["project_id", "project_name", "project_key"]
            if project_identifier.get(k)
        ]
        if len(project_keys) != 1:
            return json.dumps(
                {
                    "success": False,
                    "error": "Exactly one identifier key required for project_identifier (project_id, project_name, or project_key).",
                }
            )

        # 2. Flexible Project Identification
        target_project = None
        if project_identifier.get("project_id"):
            target_project = projects.get(project_identifier["project_id"])
        elif project_identifier.get("project_name"):
            target_project = next(
                (
                    p
                    for p in projects.values()
                    if p["project_name"] == project_identifier["project_name"]
                ),
                None,
            )
        elif project_identifier.get("project_key"):
            target_project = next(
                (
                    p
                    for p in projects.values()
                    if p["project_key"] == project_identifier["project_key"]
                ),
                None,
            )

        if not target_project:
            return json.dumps({"success": False, "error": "Target project not found."})

        project_id = target_project["project_id"]
        project_owner_id = target_project.get("project_owner_user_id")

        # 3. Process User Identifiers
        removed_count = 0
        errors = []

        for u_ident in user_identifiers:
            target_user = None
            if u_ident.get("user_id"):
                target_user = users.get(u_ident["user_id"])
            elif u_ident.get("username"):
                target_user = next(
                    (u for u in users.values() if u["username"] == u_ident["username"]),
                    None,
                )
            elif u_ident.get("email"):
                target_user = next(
                    (u for u in users.values() if u["email"] == u_ident["email"]), None
                )

            if not target_user:
                errors.append(f"User identified by {u_ident} not found.")
                continue

            u_id = target_user["user_id"]

            # Integrity Guard 1: Cannot remove the Project Owner
            if str(u_id) == str(project_owner_id):
                errors.append(
                    f"Cannot remove User '{target_user['username']}' because they are the current Project Owner. Transfer ownership first."
                )
                continue

            # Integrity Guard 2: Verify membership exists
            membership_key = next(
                (
                    k
                    for k, v in members.items()
                    if str(v["user_id"]) == str(u_id)
                    and str(v["project_id"]) == str(project_id)
                ),
                None,
            )

            if not membership_key:
                errors.append(
                    f"User '{target_user['username']}' is not a member of project '{target_project['project_name']}'."
                )
                continue

            # Integrity Guard 3: Pending Work Items
            # A user cannot be removed if they have open/active tasks assigned in this project.
            has_pending_work = any(
                str(wi["assignee_user_id"]) == str(u_id)
                and str(wi["project_id"]) == str(project_id)
                and wi["status"] in ["open", "in_progress", "pending_review"]
                for wi in work_items.values()
            )

            if has_pending_work:
                errors.append(
                    f"User '{target_user['username']}' cannot be removed: pending work items must be completed or reassigned first."
                )
                continue

            # 4. Logic: Remove from project_members table
            del members[membership_key]
            removed_count += 1
        target_project["updated_at"] = now
        return json.dumps(
            {
                "success": removed_count > 0,
                "message": f"Successfully removed {removed_count} user(s) from project '{target_project['project_name']}'.",
                "errors": errors if errors else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "remove_users_from_project",
                "description": "Formally revokes user access and association with a specific project by purging records from the membership registry, provided the users are not current project owners and have no outstanding work items in an active or pending state within that project's scope.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_identifiers": {
                            "type": "array",
                            "description": "A list of identification objects used to locate the users to be offboarded.",
                            "items": {
                                "type": "object",
                                "description": "Criteria for identifying an individual user (id, username, or email).",
                                "properties": {
                                    "user_id": {
                                        "type": "string",
                                        "description": "The unique system UUID.",
                                    },
                                    "username": {
                                        "type": "string",
                                        "description": "The unique user handle.",
                                    },
                                    "email": {
                                        "type": "string",
                                        "description": "The registered corporate email.",
                                    },
                                },
                            },
                        },
                        "project_identifier": {
                            "type": "object",
                            "description": "Criteria used to target the specific project container for removal.",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "The project's system UUID.",
                                },
                                "project_name": {
                                    "type": "string",
                                    "description": "The formal name of the project.",
                                },
                                "project_key": {
                                    "type": "string",
                                    "description": "The technical key (e.g., DEPT-2026-TITAN).",
                                },
                            },
                        },
                    },
                    "required": ["user_identifiers", "project_identifier"],
                },
            },
        }
