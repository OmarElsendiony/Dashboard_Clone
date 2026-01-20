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
        issue_type: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        issues = data.get("issues", {})

        # Validate issue_id
        if not issue_id:
            return json.dumps({"success": False, "error": "Missing required parameter: issue_id"})

        if not isinstance(issue_id, str):
            return json.dumps({"success": False, "error": "issue_id must be a string"})

        issue_id = str(issue_id).strip()

        if not issue_id:
            return json.dumps({"success": False, "error": "issue_id cannot be empty"})

        # Find the issue
        if issue_id not in issues:
            return json.dumps({
                "success": False,
                "error": f"Issue with ID '{issue_id}' not found"
            })

        issue = issues[issue_id]

        # Track if any updates were made
        updates_applied = False

        # Validate and apply title update
        if title is not None:
            if not isinstance(title, str) or not title.strip():
                return json.dumps({"success": False, "error": "title must be a non-empty string"})
            issue["title"] = title.strip()
            updates_applied = True

        # Validate and apply description update
        if description is not None:
            if not isinstance(description, str):
                return json.dumps({"success": False, "error": "description must be a string"})
            issue["description"] = description.strip()
            updates_applied = True

        # Validate and apply issue_type update
        if issue_type is not None:
            allowed_issue_types = {"bug", "feature",
                                   "documentation", "question", "enhancement"}
            if not isinstance(issue_type, str):
                return json.dumps({"success": False, "error": "issue_type must be a string"})
            issue_type_val = issue_type.strip().lower()
            if issue_type_val not in allowed_issue_types:
                return json.dumps({
                    "success": False,
                    "error": f"issue_type must be one of: {', '.join(sorted(allowed_issue_types))}"
                })
            issue["issue_type"] = issue_type_val
            updates_applied = True

        # Validate and apply priority update
        if priority is not None:
            allowed_priorities = {"low", "medium", "high", "critical"}
            if not isinstance(priority, str):
                return json.dumps({"success": False, "error": "priority must be a string"})
            priority_val = priority.strip().lower()
            if priority_val not in allowed_priorities:
                return json.dumps({
                    "success": False,
                    "error": f"priority must be one of: {', '.join(sorted(allowed_priorities))}"
                })
            issue["priority"] = priority_val
            updates_applied = True

        # Validate and apply status update
        if status is not None:
            allowed_statuses = {"open", "closed", "in_progress"}
            if not isinstance(status, str):
                return json.dumps({"success": False, "error": "status must be a string"})
            status_val = status.strip().lower()
            if status_val not in allowed_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"status must be one of: {', '.join(sorted(allowed_statuses))}"
                })

            # Handle closed_at timestamp
            timestamp = "2026-01-01T23:59:00"
            if status_val == "closed" and issue.get("status") != "closed":
                issue["closed_at"] = timestamp
            elif status_val != "closed" and issue.get("status") == "closed":
                issue["closed_at"] = None

            issue["status"] = status_val
            updates_applied = True

        if not updates_applied:
            return json.dumps({
                "success": False,
                "error": "No valid fields supplied for update"
            })

        # Update the updated_at timestamp
        timestamp = "2026-01-01T23:59:00"
        issue["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "message": f"Issue '{issue_id}' updated successfully",
            "issue_data": issue
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_issue",
                "description": "Updates an existing issue in a repository. Supports partial updates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "The ID of the issue to update.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title of the issue.",
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description of the issue.",
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "The type of issue.",
                            "enum": ["bug", "feature", "documentation", "question", "enhancement"]
                        },
                        "priority": {
                            "type": "string",
                            "description": "The priority of the issue. ",
                            "enum": ["low", "medium", "high", "critical"]
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the issue.",
                            "enum": ["open", "closed", "in_progress"]
                        },
                    },
                    "required": ["issue_id"],
                },
            },
        }
