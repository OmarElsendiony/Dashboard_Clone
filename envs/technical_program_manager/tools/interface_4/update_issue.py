import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class UpdateIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        parent_issue_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        assignee_user_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        start_date: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not issue_id:
            return json.dumps(
                {"success": False, "error": "Update requires: issue_id"}
            )

        if not any([title, description, parent_issue_id, sprint_id, assignee_user_id, status, priority, due_date, start_date]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field to update must be provided",
                }
            )

        valid_statuses = ["open", "in_progress", "blocked", "done", "closed"]
        valid_priorities = ["low", "medium", "high", "critical"]

        work_items = data.get("work_items", {})
        sprints = data.get("sprints", {})
        users = data.get("users", {})
        project_members = data.get("project_members", {})

        wid = str(issue_id).strip()
        item = work_items.get(wid)
        if item is None:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Issue '{wid}' not found",
                }
            )

        current_status = str(item.get("status", ""))
        if current_status in ["done", "closed"]:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot update issue with status '{current_status}'",
                }
            )

        item_project_id = str(item.get("project_id", ""))

        if title is not None:
            item["title"] = str(title).strip()

        if description is not None:
            item["description"] = str(description).strip()

        if status is not None:
            status_val = str(status).strip()
            if status_val not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_val}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )
            # Enforce transition rules (skip if status unchanged)
            valid_transitions = {
                "open": ["in_progress"],
                "in_progress": ["open", "done", "blocked"],
                "blocked": ["in_progress"],
            }
            if status_val != current_status:
                allowed = valid_transitions.get(current_status, [])
                if status_val not in allowed:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid status transition from '{current_status}' to '{status_val}'",
                        }
                    )
            item["status"] = status_val

        if priority is not None:
            priority_val = str(priority).strip()
            if priority_val not in valid_priorities:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid priority '{priority_val}'. Valid values: {', '.join(valid_priorities)}",
                    }
                )
            item["priority"] = priority_val

        if sprint_id is not None:
            sid = str(sprint_id).strip()
            sprint = sprints.get(sid)
            if sprint is None:
                return json.dumps({"success": False, "error": f"Sprint '{sid}' not found"})
            if str(sprint.get("project_id", "")) != item_project_id:
                return json.dumps({"success": False, "error": f"Sprint '{sid}' does not belong to project '{item_project_id}'"})
            item["sprint_id"] = sid

        if assignee_user_id is not None:
            aid = str(assignee_user_id).strip()
            if aid not in users:
                return json.dumps({"success": False, "error": f"User '{aid}' not found"})
            if str(users[aid].get("status", "")) != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User '{aid}' is not active. Current status: {str(users[aid].get('status', ''))}",
                    }
                )
            is_member = False
            for pm in project_members.values():
                if str(pm.get("user_id", "")) == aid and str(pm.get("project_id", "")) == item_project_id:
                    is_member = True
                    break
            if not is_member:
                return json.dumps({"success": False, "error": f"User '{aid}' is not a member of project '{item_project_id}'"})
            item["assignee_user_id"] = aid

        if parent_issue_id is not None:
            pid = str(parent_issue_id).strip()
            if pid.lower() == "none":
                if str(item.get("type", "")) == "subtask":
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Subtasks must have a parent issue. Cannot remove parent link.",
                        }
                    )
                item["parent_work_item_id"] = None
            else:
                parent_item = work_items.get(pid)
                if parent_item is None:
                    return json.dumps({"success": False, "error": f"Parent issue '{pid}' not found"})
                if str(parent_item.get("project_id", "")) != item_project_id:
                    return json.dumps({"success": False, "error": "Parent issue must be in the same project"})
                current_type = str(item.get("type", ""))
                parent_type = str(parent_item.get("type", ""))
                if current_type == "subtask" and parent_type not in ["story", "task"]:
                    return json.dumps({"success": False, "error": f"Subtask parent must be a story or task, got '{parent_type}'"})
                if current_type in ["story", "task"] and parent_type != "epic":
                    return json.dumps({"success": False, "error": f"Story/task parent must be an epic, got '{parent_type}'"})
                item["parent_work_item_id"] = pid

        if due_date is not None:
            item["due_date"] = str(due_date).strip()

        if start_date is not None:
            item["start_date"] = str(start_date).strip()

        item["updated_at"] = timestamp

        response = {
            "issue_id": str(item.get("work_item_id", "")),
            "type": str(item.get("type", "")),
            "title": str(item.get("title", "")),
            "description": str(item.get("description", "")) if item.get("description") else None,
            "parent_issue_id": str(item.get("parent_work_item_id", "")) if item.get("parent_work_item_id") else None,
            "sprint_id": str(item.get("sprint_id", "")) if item.get("sprint_id") else None,
            "assignee_user_id": str(item.get("assignee_user_id", "")) if item.get("assignee_user_id") else None,
            "status": str(item.get("status", "")),
            "priority": str(item.get("priority", "")) if item.get("priority") else None,
            "due_date": str(item.get("due_date", "")) if item.get("due_date") else None,
            "start_date": str(item.get("start_date", "")) if item.get("start_date") else None,
            "created_at": str(item.get("created_at", "")),
            "updated_at": str(item.get("updated_at", "")),
            "project_id": str(item.get("project_id", "")),
        }
        return json.dumps({"success": True, "issue": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_issue",
                "description": "Updates an existing issue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "Unique issue identifier.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Issue title",
                        },
                        "description": {
                            "type": "string",
                            "description": "Issue description",
                        },
                        "parent_issue_id": {
                            "type": "string",
                            "description": "Parent issue identifier (issue_id). Pass 'none' to remove the parent link.",
                        },
                        "sprint_id": {
                            "type": "string",
                            "description": "Sprint identifier (sprint_id).",
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "Assignee user identifier (user_id).",
                        },
                        "status": {
                            "type": "string",
                            "description": "Issue status.",
                            "enum": ["open", "in_progress", "blocked", "done", "closed"],
                        },
                        "priority": {
                            "type": "string",
                            "description": "Issue priority",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date timestamp",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date timestamp",
                        },
                    },
                    "required": ["issue_id"],
                    "anyOf": [
                        {"required": ["title"]},
                        {"required": ["description"]},
                        {"required": ["parent_issue_id"]},
                        {"required": ["sprint_id"]},
                        {"required": ["assignee_user_id"]},
                        {"required": ["status"]},
                        {"required": ["priority"]},
                        {"required": ["due_date"]},
                        {"required": ["start_date"]},
                    ],
                },
            },
        }
