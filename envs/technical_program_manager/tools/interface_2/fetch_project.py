import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class FetchProject(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_name: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not project_name:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'project_name'"
            })

        projects_dict = data.get("projects", {})

        if not isinstance(projects_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'projects' must be a dict"
            })

        project_name_clean = str(project_name).strip()

        project_match = None
        matched_project_id = None

        for pid, project_data in projects_dict.items():
            if str(project_data.get("project_name", "")).strip() == project_name_clean:
                project_match = project_data
                matched_project_id = pid
                break

        if not project_match:
            return json.dumps({
                "success": False,
                "error": f"Project with name '{project_name_clean}' not found"
            })

        response_project = {
            "project_id": str(matched_project_id),
            "project_key": str(project_match.get("project_key", "")),
            "project_name": str(project_match.get("project_name", "")),
            "description": str(project_match.get("description", "")),
            "status": str(project_match.get("status", "")),
            "project_owner_user_id": str(project_match.get("project_owner_user_id", "")),
            "created_at": str(project_match.get("created_at", "")),
            "updated_at": str(project_match.get("updated_at", "")),
            "closed_at": str(project_match.get("closed_at", ""))
        }

        return json.dumps({
            "success": True,
            "project": response_project
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_project",
                "description": "Retrieves project details including ownership and status. "
                               "This function validates that a project exists and confirms its current state. "
                               "Use this before executing TPM workflow operations such as task planning, ownership validation, "
                               "status updates, escalation handling, or project closure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "The unique name of the project to retrieve."
                        }
                    },
                    "required": ["project_name"]
                }
            }
        }
