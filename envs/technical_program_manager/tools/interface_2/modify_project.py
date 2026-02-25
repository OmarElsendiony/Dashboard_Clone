import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ModifyProject(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        status: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not project_id:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: 'project_id'"}
            )

        if not status:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: 'status'"}
            )

        projects_dict = data.get("projects", {})

        if not isinstance(projects_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'projects' must be a dict",
                }
            )

        project_id_clean = str(project_id).strip()
        status_clean = str(status).strip().lower()

        if status_clean.lower() not in ["in_progress", "closed"]:
            return json.dumps({
                "success": False,
                "error": "Invalid status. Only 'in_progress' or 'closed' are allowed."
            })

        if project_id_clean not in projects_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with id '{project_id_clean}' not found",
                }
            )

        project_record = projects_dict[project_id_clean]
        current_status = str(project_record.get("status", "")).strip()

        if current_status.lower() == status_clean.lower():
            return json.dumps({
                "success": False,
                "error": f"The project is already {current_status}"
            })

        if current_status in ["blocked", "closed", "inactive"]:
            return json.dumps({
                "success": False,
                "error": "The project cannot be progressed or closed as it is blocked, closed or inactive"
            })
        
        project_record["status"] = status_clean
        timestamp = "2026-02-11T23:59:00"
        project_record["updated_at"] = timestamp

        if status_clean.lower() == "closed":
            project_record["closed_at"] = timestamp 

        projects_dict[project_id_clean] = project_record

        response_project = {
            "project_id": str(project_id_clean),
            "project_key": str(project_record.get("project_key", "")),
            "project_name": str(project_record.get("project_name", "")),
            "description": str(project_record.get("description", "")),
            "status": str(project_record.get("status", "")),
            "project_owner_user_id": str(
                project_record.get("project_owner_user_id", "")
            ),
            "created_at": str(project_record.get("created_at", "")),
            "updated_at": str(project_record.get("updated_at", "")),
            "closed_at": str(project_record.get("closed_at", "")),
        }

        return json.dumps({"success": True, "project": response_project})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_project",
                "description":  "Modifies the project status to 'in_progress' or 'closed'. "
                                "This function validates that a project exists and allows its status to be updated to 'in_progress' or 'closed'. "
                                "Use this function to update the project status after creation or to close the project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project.",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["in_progress", "closed"],
                            "description": "The lifecycle status of the project."
                        }
                    },
                    "required": ["project_id", "status"],
                },
            },
        }
