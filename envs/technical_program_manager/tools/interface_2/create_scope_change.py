import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateScopeChange(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        description: str,
    ) -> str:

        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not project_id or not str(project_id).strip():
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'project_id'"
            })

        if not description or not str(description).strip():
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'description'"
            })

        project_id_str = str(project_id).strip()
        description_str = str(description).strip()

        scope_changes_dict = data.get("scope_changes", {})
        projects_dict = data.get("projects", {})

        if not isinstance(scope_changes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'scope_changes' must be a dict"
            })

        if not isinstance(projects_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'projects' must be a dict"
            })

        if project_id_str not in projects_dict:
            return json.dumps({
                "success": False,
                "error": f"Project with ID '{project_id_str}' not found"
            })

        project = projects_dict.get(project_id_str, {})
        if not isinstance(project, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid project structure for '{project_id_str}'"
            })

        project_status = str(project.get("status", "")).strip().lower()
        if project_status != "open":
            return json.dumps({
                "success": False,
                "error": (
                    f"Scope changes can only be created for open projects."
                )
            })

        requester_id = str(project.get("project_owner_user_id", "")).strip() or ""

        new_scope_change_id = str(generate_id(scope_changes_dict))

        new_scope_change = {
            "scope_change_id": str(new_scope_change_id),
            "project_id": str(project_id_str),
            "description": str(description_str),
            "requester_id": str(requester_id),
            "approver_id": "",
            "status": "pending_decision",
            "submitted_at": str(timestamp),
        }

        scope_changes_dict[new_scope_change_id] = new_scope_change
        data["scope_changes"] = scope_changes_dict

        return json.dumps({
            "success": True,
            "scope_change": new_scope_change,
            "message": (
                f"Scope change request created successfully with ID "
                f"'{new_scope_change_id}' for project '{project_id_str}'"
            ),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_scope_change",
                "description":
                    "Creates a scope change request for an open project. "
                    "The request is recorded with status 'pending_decision' and "
                    "can later be reviewed for approval or rejection. "
                    "Use this tool when proposing changes in the scope of your project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project."
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the proposed scope change."
                        },
                    },
                    "required": [
                        "project_id",
                        "description"
                    ],
                },
            },
        }
