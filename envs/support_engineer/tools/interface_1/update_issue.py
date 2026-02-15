import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        issue_id: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        status: Optional[str] = None,
        issue_type: Optional[str] = None,
        priority: Optional[str] = None,
        repository_id: Optional[int] = None,
        reproduction_verified: Optional[bool] = None,
        reproduction_env: Optional[str] = None,
        originating_ticket_id: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not issue_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'issue_id' is required."
            })

        issues = data.get("issues", {})
        repositories = data.get("repositories", {})

        if not isinstance(issues, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'issues' must be a dictionary"
            })

        if repository_id is not None and str(repository_id) not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: repository_id '{repository_id}' not found."
            })

        if originating_ticket_id is not None:
            if not isinstance(originating_ticket_id, str) or not originating_ticket_id.strip():
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: originating_ticket_id must be a non-empty string when provided."
                })

        issue_key = str(issue_id)
        issue = issues.get(issue_key)

        if issue is None:
            issue = issues.get(issue_id) if isinstance(issue_id, int) else None

        if issue is None:
            for v in issues.values():
                if isinstance(v, dict) and str(v.get("issue_id", "")) == issue_key:
                    issue = v
                    break

        if issue is None:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: issue_id '{issue_id}' not found."
            })

        if (
            title is None
            and body is None
            and status is None
            and issue_type is None
            and priority is None
            and repository_id is None
            and reproduction_verified is None
            and reproduction_env is None
            and originating_ticket_id is None
        ):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: At least one field must be provided to update."
            })

        is_change_detected = False

        if repository_id is not None:
            new_val = int(repository_id) if isinstance(repository_id, int) else repository_id
            if issue.get("repository_id") != new_val:
                is_change_detected = True

        if title is not None:
            if not isinstance(title, str):
                return json.dumps({"success": False, "error": "Invalid Argument: title must be a string."})
            if issue.get("title") != title:
                is_change_detected = True

        if body is not None:
            if not isinstance(body, str):
                return json.dumps({"success": False, "error": "Invalid Argument: body must be a string."})
            if issue.get("body") != body:
                is_change_detected = True

        valid_statuses = ["open", "in_progress", "resolved"]
        if status is not None:
            if not isinstance(status, str) or not status.strip():
                return json.dumps({"success": False, "error": "Invalid Argument: status must be a non-empty string."})
            final_status = status.strip().lower()
            if final_status not in valid_statuses:
                return json.dumps({"success": False, "error": f"Invalid Argument: Invalid status value. Valid values are: {valid_statuses}"})
            if issue.get("status") != final_status:
                is_change_detected = True

        valid_issue_types = ["bug", "configuration", "incident", "feature"]
        if issue_type is not None:
            if not isinstance(issue_type, str) or not issue_type.strip():
                return json.dumps({"success": False, "error": "Invalid Argument: issue_type must be a non-empty string."})
            final_type = issue_type.strip().lower()
            if final_type not in valid_issue_types:
                return json.dumps({"success": False, "error": f"Invalid Argument: Invalid issue_type value. Valid values are: {valid_issue_types}"})
            if issue.get("type") != final_type:
                is_change_detected = True

        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority is not None:
            if not isinstance(priority, str) or not priority.strip():
                return json.dumps({"success": False, "error": "Invalid Argument: priority must be a non-empty string."})
            final_priority = priority.strip().lower()
            if final_priority not in valid_priorities:
                return json.dumps({"success": False, "error": f"Invalid Argument: Invalid priority value. Valid values are: {valid_priorities}"})
            if issue.get("priority") != final_priority:
                is_change_detected = True

        if reproduction_verified is not None:
            if not isinstance(reproduction_verified, bool):
                return json.dumps({"success": False, "error": "Invalid Argument: reproduction_verified must be a boolean."})
            if issue.get("reproduction_verified") != reproduction_verified:
                is_change_detected = True

        valid_envs = ["staging", "test"]
        if reproduction_env is not None:
            if not isinstance(reproduction_env, str) or not reproduction_env.strip():
                return json.dumps({"success": False, "error": "Invalid Argument: reproduction_env must be a non-empty string."})
            final_env = reproduction_env.strip().lower()
            if final_env not in valid_envs:
                return json.dumps({"success": False, "error": f"Invalid Argument: Invalid env value. Valid values are: {valid_envs}"})
            if issue.get("reproduction_env") != final_env:
                is_change_detected = True

        if originating_ticket_id is not None:
            final_ticket = originating_ticket_id.strip()
            if issue.get("originating_ticket_id") != final_ticket:
                is_change_detected = True

        if not is_change_detected:
            return json.dumps({
                "success": False,
                "error": "same update Detected",
                "message": f"No-Op: Issue '{issue_id}' already has the provided values. No update performed."
            })

        timestamp = "2026-02-02 23:59:00"

        if repository_id is not None:
            issue["repository_id"] = int(repository_id) if isinstance(repository_id, int) else repository_id

        if title is not None:
            issue["title"] = title

        if body is not None:
            issue["body"] = body
            issue["description"] = body

        if status is not None:
            issue["status"] = status.strip().lower()

        if issue_type is not None:
            issue["type"] = issue_type.strip().lower()

        if priority is not None:
            issue["priority"] = priority.strip().lower()

        if reproduction_verified is not None:
            issue["reproduction_verified"] = reproduction_verified

        if reproduction_env is not None:
            issue["reproduction_env"] = reproduction_env.strip().lower()

        if originating_ticket_id is not None:
            issue["originating_ticket_id"] = originating_ticket_id.strip()

        issue["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "issue": issue,
            "message": f"Issue '{issue_id}' updated successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_issue",
                "description": (
                    "Updates an existing engineering issue by modifying one or more tracked fields."
                    "PURPOSE: Keeps issue records accurate and up to date as new triage details, progress, or corrections become available."
                    "WHEN TO USE: When an issue already exists and requires updates to status, priority, categorization, reproduction data, or description."
                    "RETURNS: The updated issue record reflecting the applied changes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "integer",
                            "description": "The unique ID of the issue to update."
                        },
                        "title": {
                            "type": "string",
                            "description": "New issue title (optional )"
                        },
                        "body": {
                            "type": "string",
                            "description": "New issue body/description text (optional )"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["open", "in_progress", "resolved"],
                            "description": "Updated issue status (optional )"
                        },
                        "issue_type": {
                            "type": "string",
                            "enum": ["bug", "configuration", "incident", "feature"],
                            "description": "Updated issue type/category (optional )"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Updated issue priority (optional )"
                        },
                        "repository_id": {
                            "type": "integer",
                            "description": "Updated repository ID for the issue (optional )"
                        },
                        "reproduction_verified": {
                            "type": "boolean",
                            "description": "Whether the issue reproduction has been verified (optional )"
                        },
                        "reproduction_env": {
                            "type": "string",
                            "enum": ["staging", "test"],
                            "description": "Environment used for reproduction (optional )"
                        },
                        "originating_ticket_id": {
                            "type": "string",
                            "description": "Ticket ID that originated the issue (optional )"
                        }
                    },
                    "required": ["issue_id"]
                }
            }
        }
