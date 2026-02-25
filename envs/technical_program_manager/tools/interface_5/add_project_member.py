import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddProjectMember(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        member_identifier: Dict[str, str],
        project_identifier: Dict[str, str],
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not isinstance(member_identifier, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "member_identifier must be a dictionary object.",
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

        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)

        member_keys = [
            k for k in ["user_id", "username", "email"] if member_identifier.get(k)
        ]
        if len(member_keys) != 1:
            return json.dumps(
                {
                    "success": False,
                    "error": "Exactly one identifier key required for member_identifier",
                }
            )

        project_keys = [
            k
            for k in ["project_id", "project_name", "project_key"]
            if project_identifier.get(k)
        ]
        if len(project_keys) != 1:
            return json.dumps(
                {
                    "success": False,
                    "error": "Exactly one identifier key required for project_identifier",
                }
            )

        # Flexible User Identification
        target_user = None
        if member_identifier.get("user_id"):
            target_user = users.get(member_identifier["user_id"])
        elif member_identifier.get("username"):
            target_user = next(
                (
                    u
                    for u in users.values()
                    if u["username"] == member_identifier["username"]
                ),
                None,
            )
        elif member_identifier.get("email"):
            target_user = next(
                (u for u in users.values() if u["email"] == member_identifier["email"]),
                None,
            )

        if not target_user:
            return json.dumps(
                {"success": False, "error": "Member to add not found in user registry."}
            )

        # Check if user is inactive
        if target_user.get("status") == "inactive":
            return json.dumps(
                {"success": False, "error": "Cannot add inactive user to project."}
            )

        # Flexible Project Identification
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

        # Check if project is closed
        if target_project.get("status") == "closed":
            return json.dumps(
                {"success": False, "error": "Cannot add members to a closed project."}
            )

        # Idempotency Check: Verify if user is already a member
        user_id = target_user["user_id"]
        project_id = target_project["project_id"]

        is_already_member = any(
            str(m["user_id"]) == str(user_id) and str(m["project_id"]) == str(project_id)
            for m in members.values()
        )
        if is_already_member:
            return json.dumps(
                {
                    "success": True,
                    "message": f"User {target_user['username']} is already a member of {target_project['project_name']}.",
                }
            )

        # Logic: Create entry in project_members
        new_member_id = generate_id(members)
        new_entry = {
            "project_member_id": new_member_id,
            "user_id": str(user_id),
            "project_id": str(project_id),
            "joined_at": now,
        }

        members[new_member_id] = new_entry

        return json.dumps(
            {
                "success": True,
                "message": f"User '{target_user['username']}' successfully added to project '{target_project['project_name']}'.",
                "membership": new_entry,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_project_member",
                "description": "To formally link an authorized user to a project record. This establishes the user's context within the project's execution and resource pool. Mandatory for project onboarding, adding subject matter experts to a project, or scaling team capacity based on workload audits.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "member_identifier": {
                            "type": "object",
                            "description": "A lookup dictionary used to locate the specific user account.",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "The unique system UUID for the user. Use if the ID is already known from previous queries.",
                                },
                                "username": {
                                    "type": "string",
                                    "description": "The unique handle for the user. Ideal for human-initiated requests.",
                                },
                                "email": {
                                    "type": "string",
                                    "description": "The unique registered corporate email address of a user.",
                                },
                            },
                        },
                        "project_identifier": {
                            "type": "object",
                            "description": "A lookup dictionary used to target the correct project container.",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "The internal system UUID for the project.",
                                },
                                "project_name": {
                                    "type": "string",
                                    "description": "The full, formal name of the project.",
                                },
                                "project_key": {
                                    "type": "string",
                                    "description": "The unique technical project key.",
                                },
                            },
                        },
                    },
                    "required": ["member_identifier", "project_identifier"],
                },
            },
        }
