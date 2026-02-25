import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetSprints(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        sprint_id: Optional[str] = None,
        sprint_name: Optional[str] = None,
        state: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([sprint_id, sprint_name, state, project_id]):
            return json.dumps({
                "success": False,
                "error": "At least one filter parameter must be provided",
            })

        if state is not None:
            state_str = str(state).strip()
            valid_states = ["future", "active", "completed", "closed"]
            if state_str not in valid_states:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid state '{state_str}'. Valid values: {', '.join(valid_states)}",
                    }
                )
        else:
            state_str = None

        sprint_id_str = str(sprint_id).strip() if sprint_id else None
        sprint_name_str = str(sprint_name).strip() if sprint_name else None
        project_id_str = str(project_id).strip() if project_id else None

        sprints = data.get("sprints", {})
        projects = data.get("projects", {})

        if project_id_str is not None and project_id_str not in projects:
            return json.dumps({"success": False, "error": f"Project '{project_id_str}' not found"})

        results = []
        for sprint in sprints.values():
            if sprint_id_str is not None and str(sprint.get("sprint_id", "")) != sprint_id_str:
                continue

            if sprint_name_str is not None and sprint_name_str.lower() != str(sprint.get("sprint_name", "")).lower():
                continue

            if state_str is not None and str(sprint.get("state", "")) != state_str:
                continue

            if project_id_str is not None and str(sprint.get("project_id", "")) != project_id_str:
                continue

            filtered_sprint = {
                "sprint_id": str(sprint.get("sprint_id", "")),
                "sprint_name": str(sprint.get("sprint_name", "")),
                "state": str(sprint.get("state", "")),
                "start_date": str(sprint.get("start_date", "")) if sprint.get("start_date") else None,
                "end_date": str(sprint.get("end_date", "")) if sprint.get("end_date") else None,
                "created_at": str(sprint.get("created_at", "")),
                "updated_at": str(sprint.get("updated_at", "")),
                "project_id": str(sprint.get("project_id", "")),
            }
            results.append(filtered_sprint)
        results.sort(key=lambda x: int(x["sprint_id"]))
        return json.dumps({"success": True, "sprints": results, "count": int(len(results))})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_sprints",
                "description": "Retrieves sprint records based on optional filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sprint_id": {
                            "type": "string",
                            "description": "Filter by the exact unique sprint identifier (sprint_id).",
                        },
                        "sprint_name": {
                            "type": "string",
                            "description": "Filter by sprint name (exact, case-insensitive).",
                        },
                        "state": {
                            "type": "string",
                            "description": "Filter by sprint state. Default for new sprints is 'future'.",
                            "enum": ["future", "active", "completed", "closed"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter by the project identifier (project_id).",
                        },
                    },
                    "anyOf": [
                        {"required": ["sprint_id"]},
                        {"required": ["sprint_name"]},
                        {"required": ["state"]},
                        {"required": ["project_id"]},
                    ],
                    "required": [],
                },
            },
        }
