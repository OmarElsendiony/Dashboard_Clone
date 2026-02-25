import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateNewIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        type: str,
        project_id: str,
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

        if not title:
            return json.dumps({"success": False, "error": "Missing required field: title"})
        if not type:
            return json.dumps({"success": False, "error": "Missing required field: type"})
        if not project_id:
            return json.dumps({"success": False, "error": "Missing required field: project_id"})

        title_str = str(title).strip()
        type_str = str(type).strip()
        project_id_str = str(project_id).strip()

        valid_types = ["epic", "story", "task", "subtask"]
        valid_statuses = ["open", "in_progress", "blocked", "done", "closed"]
        valid_priorities = ["low", "medium", "high", "critical"]

        if type_str not in valid_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid type '{type_str}'. Valid values: {', '.join(valid_types)}",
                }
            )

        if status is not None:
            status_str = str(status).strip()
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )
        else:
            status_str = "open"

        if priority is not None:
            priority_str = str(priority).strip()
            if priority_str not in valid_priorities:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid priority '{priority_str}'. Valid values: {', '.join(valid_priorities)}",
                    }
                )
        else:
            priority_str = "medium"

        projects = data.get("projects", {})
        sprints = data.get("sprints", {})
        users = data.get("users", {})
        project_members = data.get("project_members", {})
        work_items = data.get("work_items", {})

        if project_id_str not in projects:
            return json.dumps({"success": False, "error": f"Project '{project_id_str}' not found"})

        project_status = str(projects[project_id_str].get("status", ""))
        if project_status not in ["open", "in_progress"]:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project '{project_id_str}' status is '{project_status}'. Must be 'open' or 'in_progress'.",
                }
            )

        if sprint_id is not None:
            sid = str(sprint_id).strip()
            sprint = sprints.get(sid)
            if sprint is None:
                return json.dumps({"success": False, "error": f"Sprint '{sid}' not found"})
            if str(sprint.get("project_id", "")) != project_id_str:
                return json.dumps({"success": False, "error": f"Sprint '{sid}' does not belong to project '{project_id_str}'"})

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
                if str(pm.get("user_id", "")) == aid and str(pm.get("project_id", "")) == project_id_str:
                    is_member = True
                    break
            if not is_member:
                return json.dumps({"success": False, "error": f"User '{aid}' is not a member of project '{project_id_str}'"})

        for item in work_items.values():
            if (
                str(item.get("title", "")).lower() == title_str.lower()
                and str(item.get("type", "")) == type_str
                and str(item.get("project_id", "")) == project_id_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Duplicate: a {type_str} with title '{title_str}' already exists in project {project_id_str}",
                    }
                )

        parent_str = str(parent_issue_id).strip() if parent_issue_id else None

        if type_str == "epic" and parent_str is not None:
            return json.dumps(
                {"success": False, "error": "Epics cannot have a parent issue"}
            )

        if type_str == "subtask":
            if parent_str is None:
                return json.dumps(
                    {"success": False, "error": "Subtasks must have a parent issue"}
                )
            parent_item = work_items.get(parent_str)
            if parent_item is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Parent issue '{parent_str}' not found",
                    }
                )
            parent_type = str(parent_item.get("type", ""))
            if parent_type not in ["story", "task"]:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Subtask parent must be a story or task, got '{parent_type}'",
                    }
                )
            if str(parent_item.get("project_id", "")) != project_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Parent issue must be in the same project",
                    }
                )

        if type_str in ["story", "task"] and parent_str is not None:
            parent_item = work_items.get(parent_str)
            if parent_item is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Parent issue '{parent_str}' not found",
                    }
                )
            if str(parent_item.get("type", "")) != "epic":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Story/task parent must be an epic, got '{str(parent_item.get('type', ''))}'",
                    }
                )
            if str(parent_item.get("project_id", "")) != project_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Parent issue must be in the same project",
                    }
                )

        if work_items:
            max_id = max(int(k) for k in work_items.keys())
            new_id = str(max_id + 1)
        else:
            new_id = "1"

        new_item = {
            "work_item_id": new_id,
            "type": type_str,
            "title": title_str,
            "description": str(description).strip() if description else None,
            "parent_work_item_id": parent_str,
            "project_id": project_id_str,
            "sprint_id": str(sprint_id).strip() if sprint_id else None,
            "assignee_user_id": str(assignee_user_id).strip() if assignee_user_id else None,
            "status": status_str,
            "priority": priority_str,
            "due_date": str(due_date).strip() if due_date else None,
            "start_date": str(start_date).strip() if start_date else None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        work_items[new_id] = new_item

        response = {
            "issue_id": str(new_item.get("work_item_id", "")),
            "type": str(new_item.get("type", "")),
            "title": str(new_item.get("title", "")),
            "description": str(new_item.get("description", "")) if new_item.get("description") else None,
            "parent_issue_id": str(new_item.get("parent_work_item_id", "")) if new_item.get("parent_work_item_id") else None,
            "sprint_id": str(new_item.get("sprint_id", "")) if new_item.get("sprint_id") else None,
            "assignee_user_id": str(new_item.get("assignee_user_id", "")) if new_item.get("assignee_user_id") else None,
            "status": str(new_item.get("status", "")),
            "priority": str(new_item.get("priority", "")),
            "due_date": str(new_item.get("due_date", "")) if new_item.get("due_date") else None,
            "start_date": str(new_item.get("start_date", "")) if new_item.get("start_date") else None,
            "created_at": str(new_item.get("created_at", "")),
            "updated_at": str(new_item.get("updated_at", "")),
            "project_id": str(new_item.get("project_id", "")),
        }
        return json.dumps({"success": True, "issue": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_issue",
                "description": "Creates a new issue in a project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Issue title",
                        },
                        "type": {
                            "type": "string",
                            "description": "Issue type",
                            "enum": ["epic", "story", "task", "subtask"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier (project_id).",
                        },
                        "description": {
                            "type": "string",
                            "description": "Issue description",
                        },
                        "parent_issue_id": {
                            "type": "string",
                            "description": "Parent issue identifier (issue_id). Subtasks must have a parent.",
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
                            "description": "Issue status. Default is 'open'.",
                            "enum": ["open", "in_progress", "blocked", "done", "closed"],
                        },
                        "priority": {
                            "type": "string",
                            "description": "Issue priority. Default is 'medium'.",
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
                    "required": ["title", "type", "project_id"],
                },
            },
        }
