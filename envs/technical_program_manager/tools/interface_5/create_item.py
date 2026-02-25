import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateItem(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        title: str,
        created_by: str,
        type: str,
        description: Optional[str] = None,
        status: str = "open",
        priority: str = "medium",
        assignee_user_id: Optional[str] = None,
        parent_work_item_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        due_date: Optional[str] = None,
        start_date: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for work_items"}
            )

        if project_id is None:
            return json.dumps({"success": False, "error": "project_id is required"})

        if not title:
            return json.dumps({"success": False, "error": "title is required"})

        if created_by is None:
            return json.dumps({"success": False, "error": "created_by is required"})

        projects = data.get("projects", {})
        project = None
        project_key_str = str(project_id)

        if project_key_str in projects:
            project_data = projects[project_key_str]
            if str(project_data.get("project_id")) == str(project_id):
                project = project_data

        if not project:
            for project_data in projects.values():
                if str(project_data.get("project_id")) == str(project_id):
                    project = project_data
                    break

        if not project:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with ID {project_id} not found",
                }
            )

        users = data.get("users", {})
        creator_exists = False

        for _user_key, user_data in users.items():
            if str(user_data.get("user_id")) == str(created_by):
                creator_exists = True
                break

        if not creator_exists:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID {created_by} not found in users table",
                }
            )

        if assignee_user_id is not None:
            assignee_exists = False

            for _user_key, user_data in users.items():
                if str(user_data.get("user_id")) == str(assignee_user_id):
                    assignee_exists = True
                    break

            if not assignee_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID {assignee_user_id} not found in users table",
                    }
                )

        if parent_work_item_id is not None:
            work_items = data.get("work_items", {})
            parent_exists = False

            for _work_item_key, work_item_data in work_items.items():
                if str(work_item_data.get("work_item_id")) == str(parent_work_item_id):
                    parent_exists = True
                    break

            if not parent_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Parent work item with ID {parent_work_item_id} not found",
                    }
                )

        if sprint_id is not None:
            sprints = data.get("sprints", {})
            sprint_exists = False

            for _sprint_key, sprint_data in sprints.items():
                if str(sprint_data.get("sprint_id")) == str(sprint_id):
                    sprint_exists = True
                    break

            if not sprint_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Sprint with ID {sprint_id} not found",
                    }
                )

        # Validate description format (SOP 4 requirement)
        if description is not None and description:
            # Check for required format: Objective: ... | Acceptance Criteria: ... | Technical Notes: ...
            description_format_pattern = re.compile(
                r"^Objective:\s+.+?\s+\|\s+Acceptance Criteria:\s+.+?\s+\|\s+Technical Notes:\s+.+$",
                re.DOTALL,
            )
            if not description_format_pattern.match(description):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Description must follow the required format: 'Objective: [Specific goal] | Acceptance Criteria: [Checklist] | Technical Notes: [Implementation detail]'",
                    }
                )

        valid_types = ["story", "task", "epic", "subtask"]
        if type not in valid_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid type '{type}'. Must be one of: {', '.join(valid_types)}",
                }
            )

        valid_statuses = [
            "open",
            "in_progress",
            "done",
            "closed",
            "blocked",
            "rejected",
            "pending_review",
            "approved",
            "backlog",
        ]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        valid_priorities = ["low", "medium", "high", "critical"]
        if priority not in valid_priorities:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}",
                }
            )

        date_format_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

        if due_date is not None:
            if not date_format_pattern.match(due_date):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid due_date format '{due_date}'. Must be in ISO format: YYYY-MM-DDTHH:MM:SS",
                    }
                )

        if start_date is not None:
            if not date_format_pattern.match(start_date):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid start_date format '{start_date}'. Must be in ISO format: YYYY-MM-DDTHH:MM:SS",
                    }
                )

        # Validate date range: start_date cannot be after due_date
        if start_date is not None and due_date is not None:
            if start_date > due_date:
                return json.dumps(
                    {
                        "success": False,
                        "error": "start_date cannot be after due_date",
                    }
                )

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        work_items = data.setdefault("work_items", {})
        work_item_id = generate_id(work_items)
        timestamp = "2026-02-11T23:59:00"

        new_work_item = {
            "work_item_id": str(work_item_id),
            "type": str(type),
            "title": str(title),
            "description": str(description) if description is not None else None,
            "parent_work_item_id": str(parent_work_item_id)
            if parent_work_item_id is not None
            else None,
            "project_id": str(project_id),
            "sprint_id": str(sprint_id) if sprint_id is not None else None,
            "assignee_user_id": str(assignee_user_id)
            if assignee_user_id is not None
            else None,
            "created_by": str(created_by),
            "status": str(status),
            "priority": str(priority),
            "due_date": str(due_date) if due_date is not None else None,
            "start_date": str(start_date) if start_date is not None else None,
            "created_at": str(timestamp),
            "updated_at": str(timestamp),
        }

        work_items[str(work_item_id)] = new_work_item

        return json.dumps(
            {
                "success": True,
                "work_item": new_work_item,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_item",
                "description": "Creates a new work item in a project. Use this to add stories, tasks, epics, or subtasks to track project work and manage the backlog.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The project ID where the work item will be created",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the work item",
                        },
                        "created_by": {
                            "type": "string",
                            "description": "The user ID of the person creating the work item",
                        },
                        "type": {
                            "type": "string",
                            "description": "The type of work item",
                            "enum": ["story", "task", "epic", "subtask"],
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the work item",
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the work item",
                            "enum": [
                                "open",
                                "in_progress",
                                "done",
                                "closed",
                                "blocked",
                                "rejected",
                                "pending_review",
                                "approved",
                                "backlog",
                            ],
                            "default": "open",
                        },
                        "priority": {
                            "type": "string",
                            "description": "The priority level of the work item",
                            "enum": ["low", "medium", "high", "critical"],
                            "default": "medium",
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "User ID to assign the work item to",
                        },
                        "parent_work_item_id": {
                            "type": "string",
                            "description": "Parent work item ID for subtasks",
                        },
                        "sprint_id": {
                            "type": "string",
                            "description": "Sprint ID to associate the work item with",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format (YYYY-MM-DDTHH:MM:SS)",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in ISO format (YYYY-MM-DDTHH:MM:SS)",
                        },
                    },
                    "required": ["project_id", "title", "created_by", "type"],
                },
            },
        }
