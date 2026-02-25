import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetIssues(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        issue_id: Optional[str] = None,
        type: Optional[str] = None,
        title: Optional[str] = None,
        parent_issue_id: Optional[str] = None,
        project_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        assignee_user_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        if not any([issue_id, type, title, parent_issue_id, project_id, sprint_id, assignee_user_id, incident_id, status]):
            return json.dumps({
                "success": False,
                "error": "At least one filter parameter must be provided",
            })

        if type is not None:
            type_str = str(type).strip()
            valid_types = ["epic", "story", "task", "subtask"]
            if type_str not in valid_types:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid type '{type_str}'. Valid values: {', '.join(valid_types)}",
                    }
                )
        else:
            type_str = None

        if status is not None:
            status_str = str(status).strip()
            valid_statuses = ["open", "in_progress", "blocked", "done", "closed"]
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )
        else:
            status_str = None

        issue_id_str = str(issue_id).strip() if issue_id else None
        title_str = str(title).strip() if title else None
        parent_str = str(parent_issue_id).strip() if parent_issue_id else None
        project_id_str = str(project_id).strip() if project_id else None
        sprint_id_str = str(sprint_id).strip() if sprint_id else None
        assignee_str = str(assignee_user_id).strip() if assignee_user_id else None
        incident_id_str = str(incident_id).strip() if incident_id else None

        work_items = data.get("work_items", {})
        incidents = data.get("incidents", {})
        projects = data.get("projects", {})
        sprints = data.get("sprints", {})
        users = data.get("users", {})

        if project_id_str is not None and project_id_str not in projects:
            return json.dumps({"success": False, "error": f"Project '{project_id_str}' not found"})

        if sprint_id_str is not None and sprint_id_str not in sprints:
            return json.dumps({"success": False, "error": f"Sprint '{sprint_id_str}' not found"})

        if assignee_str is not None and assignee_str not in users:
            return json.dumps({"success": False, "error": f"User '{assignee_str}' not found"})

        if parent_str is not None and parent_str not in work_items:
            return json.dumps({"success": False, "error": f"Issue '{parent_str}' not found"})

        if incident_id_str is not None:
            found_incident = False
            for inc in incidents.values():
                if str(inc.get("incident_id", "")) == incident_id_str:
                    found_incident = True
                    break
            if not found_incident:
                return json.dumps({"success": False, "error": f"Incident '{incident_id_str}' not found"})

        # Build set of work_item_ids linked to the given incident
        incident_work_item_ids = None
        if incident_id_str is not None:
            incident_work_item_ids = set()
            for inc in incidents.values():
                if str(inc.get("incident_id", "")) == incident_id_str:
                    wid = inc.get("work_item_id")
                    if wid is not None:
                        incident_work_item_ids.add(str(wid))

        results = []
        for item in work_items.values():
            if issue_id_str is not None and str(item.get("work_item_id", "")) != issue_id_str:
                continue

            if type_str is not None and str(item.get("type", "")) != type_str:
                continue

            if title_str is not None and title_str.lower() != str(item.get("title", "")).lower():
                continue

            if parent_str is not None:
                item_parent = item.get("parent_work_item_id")
                if item_parent is None or str(item_parent) != parent_str:
                    continue

            if project_id_str is not None and str(item.get("project_id", "")) != project_id_str:
                continue

            if sprint_id_str is not None and str(item.get("sprint_id", "")) != sprint_id_str:
                continue

            if assignee_str is not None:
                item_assignee = item.get("assignee_user_id")
                if item_assignee is None or str(item_assignee) != assignee_str:
                    continue

            if status_str is not None and str(item.get("status", "")) != status_str:
                continue

            if incident_work_item_ids is not None:
                if str(item.get("work_item_id", "")) not in incident_work_item_ids:
                    continue
            filtered_item = {
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
                "created_by": str(item.get("created_by", "")) if item.get("created_by") else None,
                "created_at": str(item.get("created_at", "")),
                "updated_at": str(item.get("updated_at", "")),
                "project_id": str(item.get("project_id", "")),
            }
            results.append(filtered_item)
        results.sort(key=lambda x: int(x["issue_id"]))
        return json.dumps({"success": True, "issues": results, "count": int(len(results))})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_issues",
                "description": "Retrieves issues based on optional filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "Filter by the exact unique issue identifier (issue_id).",
                        },
                        "type": {
                            "type": "string",
                            "description": "Filter by issue type",
                            "enum": ["epic", "story", "task", "subtask"],
                        },
                        "title": {
                            "type": "string",
                            "description": "Filter by issue title (exact, case-insensitive).",
                        },
                        "parent_issue_id": {
                            "type": "string",
                            "description": "Filter by parent issue identifier (issue_id).",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter by project identifier (project_id).",
                        },
                        "sprint_id": {
                            "type": "string",
                            "description": "Filter by sprint identifier (sprint_id).",
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "Filter by assignee user identifier (user_id).",
                        },
                        "incident_id": {
                            "type": "string",
                            "description": "Filter by linked incident identifier (incident_id).",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by issue status.",
                            "enum": ["open", "in_progress", "blocked", "done", "closed"],
                        },
                    },
                    "anyOf": [
                        {"required": ["issue_id"]},
                        {"required": ["type"]},
                        {"required": ["title"]},
                        {"required": ["parent_issue_id"]},
                        {"required": ["project_id"]},
                        {"required": ["sprint_id"]},
                        {"required": ["assignee_user_id"]},
                        {"required": ["incident_id"]},
                        {"required": ["status"]},
                    ],
                    "required": [],
                },
            },
        }
