import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateWorkItem(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        type: str,
        title: str,
        project_id: str,
        created_by: str,
        assignee_user_id: Optional[str] = None,
        status: str = "backlog",
        description: Optional[str] = None,
        parent_work_item_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        for param_name, param_value in [
            ("type", type),
            ("title", title),
            ("project_id", project_id),
            ("created_by", created_by)
        ]:
            if not param_value or not str(param_value).strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Missing required parameter: '{param_name}'",
                    }
                )

        type_str = str(type).strip().lower()
        title_str = str(title).strip()
        project_id_str = str(project_id).strip()
        created_by_str = str(created_by).strip()
        assignee_user_id_str = str(assignee_user_id).strip() if assignee_user_id else None
        status_str = str(status).strip().lower() if status else "backlog"
        description_str = str(description).strip() if description else None
        parent_work_item_id_str = (
            str(parent_work_item_id).strip() if parent_work_item_id else None
        )

        valid_types = ["task", "subtask"]
        if type_str not in valid_types:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid type '{type_str}'. "
                        f"Must be one of: {', '.join(valid_types)}"
                    ),
                }
            )

        valid_statuses = [
            "backlog"
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
        users_dict = data.get("users", {})

        if project_id_str not in projects_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with ID '{project_id_str}' not found",
                }
            )

        project = projects_dict[project_id_str]
        project_status = str(project.get("status", "")).strip().lower()
        if project_status not in ["open", "in_progress"]:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Work items can only be created for projects with status 'open' or 'in_progress'."
                        f"'Current project status: '{project_status}'"
                    ),
                }
            )

        if created_by_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{created_by_str}' not found (created_by)",
                }
            )

        if assignee_user_id_str and (assignee_user_id_str not in users_dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Assignee user with ID '{assignee_user_id_str}' not found",
                }
            )

        if assignee_user_id_str:
            assignee = users_dict[assignee_user_id_str]
            assignee_status = str(assignee.get("status", "")).strip().lower()
            if assignee_status != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Assignee user '{assignee_user_id_str}' is not active "
                            f"(status: '{assignee_status}')"
                        ),
                    }
                )

        for wi_id, wi_data in work_items_dict.items():
            if not isinstance(wi_data, dict):
                continue
            if (
                str(wi_data.get("project_id", "")).strip() == project_id_str
                and str(wi_data.get("title", "")).strip().lower() == title_str.lower()
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"A work item with the title '{title_str}' already exists "
                            f"in project '{project_id_str}' (work_item_id: {wi_id})"
                        ),
                    }
                )

        if type_str == "subtask":
            if not parent_work_item_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "A subtask requires a 'parent_work_item_id'",
                    }
                )

            if parent_work_item_id_str not in work_items_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Parent work item with ID '{parent_work_item_id_str}' not found"
                        ),
                    }
                )

            parent_item = work_items_dict[parent_work_item_id_str]

            if str(parent_item.get("project_id", "")).strip() != project_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Parent work item '{parent_work_item_id_str}' does not "
                            f"belong to project '{project_id_str}'"
                        ),
                    }
                )

            parent_type = str(parent_item.get("type", "")).strip().lower()
            if parent_type == "subtask":
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            "Depth constraint violated: a subtask cannot be a child of "
                            "another subtask. Maximum hierarchy depth is two levels "
                            "(task → subtask)."
                        ),
                    }
                )

            valid_parent_statuses = ["open", "backlog", "in_progress"]
            parent_status = str(parent_item.get("status", "")).strip().lower()
            if parent_status not in valid_parent_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Cannot create a subtask under parent work item "
                            f"'{parent_work_item_id_str}' with status '{parent_status}'. "
                            f"Parent must have one of the following statuses: "
                            f"{', '.join(valid_parent_statuses)}"
                        ),
                    }
                )

        elif type_str == "task":
            if parent_work_item_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            "A top-level task cannot have a 'parent_work_item_id'. "
                            "Use type 'subtask' to create a child work item."
                        ),
                    }
                )

        new_work_item_id = generate_id(work_items_dict)

        new_work_item = {
            "work_item_id": str(new_work_item_id),
            "type": str(type_str),
            "title": str(title_str),
            "description": str(description_str) if description_str else None,
            "parent_work_item_id": str(parent_work_item_id_str) if parent_work_item_id_str else None,
            "project_id": str(project_id_str),
            "assignee_user_id": str(assignee_user_id_str) if assignee_user_id_str else None,
            "created_by": str(created_by_str),
            "status": str(status_str),
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        work_items_dict[new_work_item_id] = new_work_item

        return json.dumps(
            {
                "success": True,
                "work_item": new_work_item,
                "message": (
                    f"Work item '{title_str}' of type '{type_str}' created successfully "
                    f"with ID '{new_work_item_id}' in project '{project_id_str}'"
                ),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_work_item",
                "description":
                    "Creates a new work item (task or subtask) within a project. "
                    "Tasks are top-level work items scoped directly to a project. "
                    "Subtasks are children of an existing task and cannot be nested further "
                    "Enforces title uniqueness within the same project, validates that the "
                    "parent task exists and is in an actionable state when creating subtasks, "
                    "and defaults status to 'backlog'. "
                    "Use this during work-breakdown and planning to decompose project "
                    "initiatives into individually trackable, executable units of work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The type of work item to create.",
                            "enum": ["task", "subtask"],
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the work item.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project this work item belongs to. ",
                        },
                        "created_by": {
                            "type": "string",
                            "description": "The user_id of the user creating the work item. ",
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "The user_id of the team member responsible for completing the work item.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status of the work item. Defaults to 'backlog'.",
                            "enum": [
                                "backlog"
                            ],
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. A detailed description of the work item.",
                        },
                        "parent_work_item_id": {
                            "type": "string",
                            "description": "The work_item_id of the parent task",
                        },
                    },
                    "required": [
                        "type",
                        "title",
                        "project_id",
                        "created_by",
                    ],
                },
            },
        }
