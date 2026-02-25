import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class RetrieveWorkItem(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        title: Optional[str] = None,
        parent_work_item_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not project_id or not str(project_id).strip():
            return json.dumps(
                {
                    "success": False,
                    "error": "Missing required parameter: 'project_id'",
                }
            )

        project_id_str = str(project_id).strip()
        title_str = str(title).strip() if title else None
        parent_work_item_id_str = (
            str(parent_work_item_id).strip() if parent_work_item_id else None
        )
        status_str = str(status).strip().lower() if status else None

        if status_str:
            valid_statuses = [
                "backlog",
                "in_progress",
                "blocked",
                "pending_review",
                "done",
            ]
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Invalid status '{status_str}'. "
                            f"Must be one of: {', '.join(valid_statuses)}"
                        ),
                    }
                )

        work_items_dict = data.get("work_items", {})
        projects_dict = data.get("projects", {})

        if project_id_str not in projects_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with ID '{project_id_str}' not found",
                }
            )

        if title_str:
            matching_work_items = []
            for _, wi_data in work_items_dict.items():
                if not isinstance(wi_data, dict):
                    continue
                if (
                    str(wi_data.get("project_id", "")).strip() == project_id_str
                    and str(wi_data.get("title", "")).strip().lower()
                    == title_str.lower()
                ):
                    wi_data_copy = wi_data.copy()
                    wi_data_copy.pop("sprint_id", None)
                    wi_data_copy.pop("document_id", None)
                    wi_data_copy.pop("priority", None)
                    matching_work_items.append(wi_data_copy)

            if not matching_work_items:
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Work item with title '{title_str}' not found "
                            f"in project '{project_id_str}'"
                        ),
                    }
                )

            return json.dumps(
                {
                    "success": True,
                    "work_items": matching_work_items,
                    "count": len(matching_work_items),
                    "message": (
                        f"Found {len(matching_work_items)} work item(s) with title "
                        f"'{title_str}' in project '{project_id_str}'"
                    ),
                }
            )

        matching_work_items = []
        for _, wi_data in work_items_dict.items():
            if not isinstance(wi_data, dict):
                continue

            if str(wi_data.get("project_id", "")).strip() != project_id_str:
                continue

            if parent_work_item_id_str is not None:
                if parent_work_item_id_str.lower() == "none":
                    if wi_data.get("parent_work_item_id") is not None:
                        continue
                else:
                    if (
                        str(wi_data.get("parent_work_item_id", "")).strip()
                        != parent_work_item_id_str
                    ):
                        continue

            if status_str:
                if str(wi_data.get("status", "")).strip().lower() != status_str:
                    continue

            wi_data_copy = wi_data.copy()
            wi_data_copy.pop("sprint_id", None)
            wi_data_copy.pop("document_id", None)
            wi_data_copy.pop("priority", None)
            matching_work_items.append(wi_data_copy)

        return json.dumps(
            {
                "success": True,
                "work_items": matching_work_items,
                "count": len(matching_work_items),
                "message": (
                    f"Retrieved {len(matching_work_items)} work item(s) "
                    f"from project '{project_id_str}'"
                ),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_work_item",
                "description": (
                    "Retrieves one or more task within a project using various query modes. "
                    "Supports: (1) finding a specific task by title within the project, "
                    "or (2) bulk fetching all task in the project with optional filtering "
                    "by parent_work_item_id or status. If title is provided, it performs an exact match search "
                    "for that title within the specified project and does not consider other filters. "
                    "Use this to validate parent tasks before creating subtasks, fetch unassigned "
                    "tasks for ownership assignment, retrieve tasks for status updates, identify "
                    "blocked work during incident management, and gather project completion metrics."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project to query.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the task to find.",
                        },
                        "parent_work_item_id": {
                            "type": "string",
                            "description": "Filter for tasks with a specific parent.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter for tasks with a specific status.",
                            "enum": [
                                "backlog",
                                "in_progress",
                                "blocked",
                                "pending_review",
                                "done",
                            ],
                        },
                    },
                    "required": ["project_id"],
                },
            },
        }
