import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetProjects(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: Optional[str] = None,
        project_key: Optional[str] = None,
        project_name: Optional[str] = None,
        status: Optional[str] = None,
        project_owner_user_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([project_id, project_key, project_name, status, project_owner_user_id]):
            return json.dumps({
                "success": False,
                "error": "At least one filter parameter must be provided",
            })

        if status is not None:
            status_str = str(status).strip()
            valid_statuses = ["open", "in_progress", "closed"]
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )
        else:
            status_str = None

        project_id_str = str(project_id).strip() if project_id else None
        project_key_str = str(project_key).strip() if project_key else None
        project_name_str = str(project_name).strip() if project_name else None
        owner_str = str(project_owner_user_id).strip() if project_owner_user_id else None

        projects = data.get("projects", {})
        project_members = data.get("project_members", {})

        results = []
        for project in projects.values():
            if project_id_str is not None and str(project.get("project_id", "")) != project_id_str:
                continue

            if project_key_str is not None and str(project.get("project_key", "")).lower() != project_key_str.lower():
                continue

            if project_name_str is not None and project_name_str.lower() != str(project.get("project_name", "")).lower():
                continue

            if status_str is not None and str(project.get("status", "")) != status_str:
                continue

            if owner_str is not None and str(project.get("project_owner_user_id", "")) != owner_str:
                continue

            users_list = []
            for pm in project_members.values():
                if str(pm.get("project_id", "")) == str(project.get("project_id", "")):
                    users_list.append({"user_id": str(pm.get("user_id", ""))})
            users_list.sort(key=lambda x: int(x["user_id"]))

            filtered_project = {
                "project_id": str(project.get("project_id", "")),
                "project_key": str(project.get("project_key", "")),
                "project_name": str(project.get("project_name", "")),
                "description": str(project.get("description", "")) if project.get("description") else None,
                "status": str(project.get("status", "")),
                "project_owner_user_id": str(project.get("project_owner_user_id", "")),
                "created_at": str(project.get("created_at", "")),
                "updated_at": str(project.get("updated_at", "")),
                "closed_at": str(project.get("closed_at", "")) if project.get("closed_at") else None,
                "project_members": users_list,
            }
            results.append(filtered_project)
        results.sort(key=lambda x: int(x["project_id"]))
        return json.dumps({"success": True, "projects": results, "count": int(len(results))})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_projects",
                "description": "Retrieves project records and associated member lists based on optional filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Filter by the exact unique project identifier (project_id).",
                        },
                        "project_key": {
                            "type": "string",
                            "description": "Filter by project key (exact, case-insensitive)",
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Filter by project name (exact, case-insensitive).",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by project status",
                            "enum": ["open", "in_progress", "closed"],
                        },
                        "project_owner_user_id": {
                            "type": "string",
                            "description": "Filter by the user_id of the project owner.",
                        },
                    },
                    "anyOf": [
                        {"required": ["project_id"]},
                        {"required": ["project_key"]},
                        {"required": ["project_name"]},
                        {"required": ["status"]},
                        {"required": ["project_owner_user_id"]},
                    ],
                    "required": [],
                },
            },
        }
