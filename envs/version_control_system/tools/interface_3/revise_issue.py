import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ReviseIssue(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        assignee_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Updates an existing issue's title, description, assignee, or status.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not issue_id:
            return json.dumps({"success": False, "error": "issue_id is required to revise an issue"})

        # Check that at least one field is provided for update
        if title is None and description is None and assignee_id is None and status is None:
            return json.dumps({"success": False, "error": "At least one field (title, description, assignee_id, status) must be provided for update"})

        # Validate status if provided
        if status is not None:
            valid_statuses = ["open", "closed", "in_progress"]
            if status not in valid_statuses:
                return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: open, closed, in_progress"})

        users = data.get("users", {})
        issues = data.get("issues", {})

        # Validate issue exists
        if str(issue_id) not in issues:
            return json.dumps({"success": False, "error": f"Issue with id '{issue_id}' not found"})

        # Validate assignee exists if provided
        if assignee_id is not None and str(assignee_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{assignee_id}' not found"})

        issue = issues[str(issue_id)]

        # Update fields if provided
        if title is not None:
            issue["title"] = title

        if description is not None:
            issue["description"] = description

        if assignee_id is not None:
            issue["assignee_id"] = assignee_id

        if status is not None:
            old_status = issue.get("status")
            issue["status"] = status

            # Set closed_at if transitioning to closed
            if status == "closed" and old_status != "closed":
                issue["closed_at"] = "2026-01-01T23:59:00"
            # Clear closed_at if reopening
            elif status != "closed" and old_status == "closed":
                issue["closed_at"] = None

        issue["updated_at"] = "2026-01-01T23:59:00"

        return json.dumps({"success": True, "result": issue})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "revise_issue",
                "description": "Updates an existing issue. Allows modifying the title, description, assignee, and status. At least one field must be provided for update.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "The unique identifier of the issue to update."
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title for the issue. Optional."
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description for the issue. Optional."
                        },
                        "assignee_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to assign to this issue. Optional."
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status for the issue. Valid values: open, closed, in_progress. Optional."
                        }
                    },
                    "required": ["issue_id"]
                }
            }
        }
