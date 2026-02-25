import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        project_key: str,
        owner_user_id: str,
        status: str,
        description: Optional[str] = None,
    ) -> str:

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format. Expected 'data' to be a dictionary."
            })

        title = str(title).strip() if title is not None else ""
        project_key = str(project_key).strip() if project_key is not None else ""
        owner_user_id = str(owner_user_id).strip() if owner_user_id is not None else ""
        status = str(status).strip() if status is not None else ""
        description = str(description).strip() if description is not None else None

        if not title:
            return json.dumps({
                "success": False,
                "error": "Invalid or missing project title."
            })

        if not project_key:
            return json.dumps({
                "success": False,
                "error": "Invalid or missing project key."
            })

        if not owner_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or missing owner_user_id."
            })

        if not status:
            return json.dumps({
                "success": False,
                "error": "Invalid or missing status."
            })

        if status != "open":
            return json.dumps({
                "success": False,
                "error": "Invalid status. The only supported status is 'open'."
            })

        projects_dict = data.setdefault("projects", {})
        users_dict = data.get("users", {})

        if not isinstance(projects_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data structure. 'projects' must be a dictionary."
            })

        if not isinstance(users_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data structure. 'users' must be a dictionary."
            })

        if owner_user_id not in users_dict:
            return json.dumps({
                "success": False,
                "error": "The specified owner_user_id does not exist."
            })

        for proj in projects_dict.values():
            if str(proj.get("project_name", "")).strip() == title:
                return json.dumps({
                    "success": False,
                    "error": "A project with this title already exists."
                })

        for proj in projects_dict.values():
            if str(proj.get("project_key", "")).strip() == project_key:
                return json.dumps({
                    "success": False,
                    "error": "A project with this key already exists."
                })

        new_project_id = str(generate_id(projects_dict))
        timestamp = "2026-02-11T23:59:00"

        project_record = {
            "project_id": str(new_project_id),
            "project_key": str(project_key),
            "project_name": str(title),
            "description": str(description),
            "status": str(status),
            "project_owner_user_id": str(owner_user_id),
            "created_at": timestamp,
            "updated_at": timestamp,
            "closed_at": None
        }

        projects_dict[new_project_id] = project_record
        return json.dumps({
            "success": True,
            "project": project_record,
            "message": "Project created successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_project",
                "description": "Create a new project record and assign an owner. "
                               "Use this tool when a Technical program manager or authorized user needs to formally create and register a project in the system. "
                               "It ensures the project is properly established with the provided details and linked to the specified owner so work can begin under a single, tracked project record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Unique name of the project to create"
                        },
                        "project_key": {
                            "type": "string",
                            "description": "Unique project identifier assigned to the project"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the project to be created"
                        },
                        "owner_user_id": {
                            "type": "string",
                            "description": "Unique identifier of the project owner."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["open"],
                            "description": "Represents the current stage of the project"
                        }
                    },
                    "required": ["title", "project_key", "owner_user_id", "status"]
                }
            }
        }