import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateProjectMeta(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any],
               project_identifier: Dict[str, str],
               updated_by_user_id: str,
               status: Optional[str] = None,
               scope: Optional[str] = None,
               project_owner_identifier: Optional[Dict[str, str]] = None,
               description: Optional[str] = None
               ) -> str:

        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)

        # 1. Basic data integrity check
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # System Epoch: 02/10/2026 23:59:00
        now = "2026-02-11T23:59:00"
        projects = data.get("projects", {})
        users = data.get("users", {})
        scopes = data.get("scope_changes", {})

        # 2. Validation: Requestor Existence
        if updated_by_user_id not in users:
            return json.dumps({"success": False, "error": f"Requesting User ID '{updated_by_user_id}' not found."})

        # 3. Flexible Project Identification Logic
        if not project_identifier:
            return json.dumps({"success": False, "error": "Project identifier is required."})

        target_project = None
        if project_identifier.get("project_id"):
            target_project = projects.get(project_identifier["project_id"])
        elif project_identifier.get("project_name"):
            target_project = next((p for p in projects.values() if p["project_name"] == project_identifier["project_name"]), None)
        elif project_identifier.get("project_key"):
            target_project = next((p for p in projects.values() if p["project_key"] == project_identifier["project_key"]), None)

        if not target_project:
            return json.dumps({"success": False, "error": "Project not found with provided identifier."})

        if not any([status, scope, project_owner_identifier, description]):
            return json.dumps({"success": False, "error": "No update applied. Provide at least one field to update."})

        # 4. Validation: Status Enum
        if status:
            valid_statuses = ['open', 'in_progress', 'blocked', 'closed']
            if status.lower() not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of {valid_statuses}"
                })
            target_project["status"] = status
            if status == "closed":
                target_project["closed_at"] = now

        # 5. Logic: Scope Change (Section 5 Implementation)
        new_scope_record = None
        if scope:
            if "Current Scope:" not in scope or "Exclusions:" not in scope or "Change Reason:" not in scope:
                return json.dumps({
                    "success": False,
                    "error": "Formatting Violation: Scope must follow the Scope Format Standard: 'Current Scope: ... | Exclusions: ... | Change Reason: ...'"
                })

            new_scope_id = generate_id(scopes)
            new_scope_record = {
                "scope_change_id": new_scope_id,
                "project_id": str(target_project["project_id"]),
                "description": str(scope),
                "requestor_id": str(updated_by_user_id),
                "approver_id": None,
                "status": "pending_decision",
                "submitted_at": now
            }
            scopes[new_scope_id] = new_scope_record

        # 6. Flexible Owner Identification Logic
        if project_owner_identifier:
            target_user = None
            u_id = project_owner_identifier.get("user_id")
            u_name = project_owner_identifier.get("username")
            u_email = project_owner_identifier.get("email")

            if u_id:
                target_user = users.get(u_id) or users.get(str(u_id))
            elif u_name:
                target_user = next((u for u in users.values() if u["username"] == u_name), None)
            elif u_email:
                target_user = next((u for u in users.values() if u["email"] == u_email), None)

            if not target_user:
                return json.dumps({"success": False, "error": f"New owner identifier {project_owner_identifier} not found."})

            if target_user["role"] != "technical_program_manager":
                return json.dumps({"success": False, "error": "Owner must be a Technical Program Manager."})

            target_project["project_owner_user_id"] = str(target_user["user_id"])

        # 7. Metadata updates
        if description:
            target_project["description"] = str(description)

        target_project["updated_at"] = now

        return json.dumps({
            "success": True,
            "message": f"Project metadata for '{target_project['project_name']}' updated successfully.",
            "project": target_project,
            "new_scope_change": new_scope_record
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_project_meta",
                "description": "Modifies a project's attributes, lifecycle states, and ownership. Ensures that scope changes are documented with rationale and that all status transitions are logged.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_identifier": {
                            "type": "object",
                            "description": "Lookup dictionary to locate the project record (id, name, or key).",
                            "properties": {
                                "project_id": {"type": "string", "description": "The unique project ID"},
                                "project_name": {"type": "string", "description": "The unique project name"},
                                "project_key": {"type": "string", "description": "The unique project key"}
                            }
                        },
                        "status": {
                            "type": "string",
                            "enum": ["open", "in_progress", "blocked", "closed"],
                            "description": "The new lifecycle state to be applied."
                        },
                        "scope": {
                            "type": "string",
                            "description": "Updated boundaries following the 'Current Scope: | Exclusions: | Change Reason:' standard."
                        },
                        "project_owner_identifier": {
                            "type": "object",
                            "description": "Lookup dictionary to identify the new project owner.",
                            "properties": {
                                "user_id": {"type": "string", "description": "The unique ID of the new project owner."},
                                "username": {"type": "string", "description": "The unique handle of the new project owner."},
                                "email": {"type": "string", "description": "The unique email address of the new project owner."}
                            }
                        },
                        "description": {
                            "type": "string",
                            "description": "A revised technical summary or business objective."
                        },
                        "updated_by_user_id": {
                            "type": "string",
                            "description": "The unique ID of the user making the changes."
                        }
                    },
                    "required": ["project_identifier", "updated_by_user_id"]
                }
            }
        }
