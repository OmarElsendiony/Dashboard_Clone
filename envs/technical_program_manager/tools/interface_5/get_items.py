import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetItems(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        assignee_user_id: Optional[str] = None,
        due_date_before: Optional[str] = None,
        updated_at_before: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for work_items"}
            )

        if (
            project_id is None
            and priority is None
            and status is None
            and assignee_user_id is None
            and due_date_before is None
            and updated_at_before is None
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one parameter (project_id, priority, status, assignee_user_id, due_date_before, or updated_at_before) is required",
                }
            )

        # Validate project exists if project_id is provided
        projects = data.get("projects", {})
        project = None
        if project_id is not None:
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
                        "error": f"Project with ID {str(project_id)} not found",
                    }
                )

        if priority is not None:
            valid_priorities = ["low", "medium", "high", "critical"]
            if priority not in valid_priorities:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}",
                    }
                )

        if status is not None:
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

        # Validate date format (YYYY-MM-DDTHH:MM:SS)
        date_format_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

        if due_date_before is not None:
            if not date_format_pattern.match(due_date_before):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid due_date_before format '{due_date_before}'. Must be in ISO format: YYYY-MM-DDTHH:MM:SS",
                    }
                )

        if updated_at_before is not None:
            if not date_format_pattern.match(updated_at_before):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid updated_at_before format '{updated_at_before}'. Must be in ISO format: YYYY-MM-DDTHH:MM:SS",
                    }
                )

        # Validate assignee_user_id exists in users table
        if assignee_user_id is not None:
            users = data.get("users", {})
            user_exists = False

            # Check if user exists by iterating through users
            for _user_key, user_data in users.items():
                if str(user_data.get("user_id")) == str(assignee_user_id):
                    user_exists = True
                    break

            if not user_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID {str(assignee_user_id)} not found in users table",
                    }
                )

        work_items = data.get("work_items", {})
        results = []

        for _work_item_id, work_item in work_items.items():
            # Filter by project_id if provided
            if project_id is not None:
                if str(work_item.get("project_id")) != str(project_id):
                    continue

            if priority and work_item.get("priority") != priority:
                continue

            if status and work_item.get("status") != status:
                continue

            if assignee_user_id is not None:
                item_assignee = work_item.get("assignee_user_id")
                if str(item_assignee) != str(assignee_user_id):
                    continue

            if due_date_before:
                item_due_date = work_item.get("due_date")
                if item_due_date:
                    if item_due_date >= due_date_before:
                        continue
                else:
                    continue

            if updated_at_before:
                item_updated_at = work_item.get("updated_at")
                if item_updated_at:
                    if item_updated_at >= updated_at_before:
                        continue
                else:
                    continue

            result_item = work_item.copy()
            # Ensure all fields are strings
            if result_item.get("work_item_id") is not None:
                result_item["work_item_id"] = str(result_item.get("work_item_id"))
            if result_item.get("project_id") is not None:
                result_item["project_id"] = str(result_item.get("project_id"))
            if result_item.get("assignee_user_id") is not None:
                result_item["assignee_user_id"] = str(
                    result_item.get("assignee_user_id")
                )
            if result_item.get("priority") is not None:
                result_item["priority"] = str(result_item.get("priority"))
            if result_item.get("status") is not None:
                result_item["status"] = str(result_item.get("status"))
            if result_item.get("title") is not None:
                result_item["title"] = str(result_item.get("title"))
            if result_item.get("description") is not None:
                result_item["description"] = str(result_item.get("description"))
            if result_item.get("due_date") is not None:
                result_item["due_date"] = str(result_item.get("due_date"))
            if result_item.get("created_at") is not None:
                result_item["created_at"] = str(result_item.get("created_at"))
            if result_item.get("updated_at") is not None:
                result_item["updated_at"] = str(result_item.get("updated_at"))

            results.append(result_item)

        response = {
            "success": True,
            "count": len(results),
            "results": results,
        }
        if project_id is not None:
            response["project_id"] = str(project_id)
        return json.dumps(response)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Retrieve work items with optional filters. Can filter by project_id to get work items for a specific project, or query all work items across projects. Perfect for backlog management, identifying critical risks, analyzing team capacity, tracking overdue items, and finding stale work. Use this to get a comprehensive view of work items filtered by project, priority, status, assignee, or date ranges.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Optional. The project ID to retrieve work items from. If provided, filters results to work items for this project only.",
                        },
                        "priority": {
                            "type": "string",
                            "description": "Filter by work item priority level",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by work item status",
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
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "Filter by the user ID of the assigned team member",
                        },
                        "due_date_before": {
                            "type": "string",
                            "description": "Find work items with a due date before this date (ISO format: YYYY-MM-DDTHH:MM:SS). Use this to identify overdue items that need attention.",
                        },
                        "updated_at_before": {
                            "type": "string",
                            "description": "Find work items last updated before this date (ISO format: YYYY-MM-DDTHH:MM:SS). Use this to identify stale or inactive work items that may need review.",
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["project_id"]},
                        {"required": ["priority"]},
                        {"required": ["status"]},
                        {"required": ["assignee_user_id"]},
                        {"required": ["due_date_before"]},
                        {"required": ["updated_at_before"]},
                    ],
                },
            },
        }
