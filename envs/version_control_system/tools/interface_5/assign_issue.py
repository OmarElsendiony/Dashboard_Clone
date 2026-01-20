import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AssignIssue(Tool):
    
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        issue_id: str,
        assignee_id: str,
    ) -> str:
      

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        issues = data.get("issues", {})
        users = data.get("users", {})

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

        # Validate assignee_id
        if not assignee_id:
            return json.dumps({"success": False, "error": "Missing required parameter: assignee_id"})

        if not isinstance(assignee_id, str):
            return json.dumps({"success": False, "error": "assignee_id must be a string"})

        assignee_id = str(assignee_id).strip()

        if not assignee_id:
            return json.dumps({"success": False, "error": "assignee_id cannot be empty"})

        # Find the assignee user
        if assignee_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{assignee_id}' not found"
            })

        assignee = users[assignee_id]

        # Check if assignee is active
        if assignee.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{assignee_id}' is not active"
            })

        # Check if issue is already assigned to this user
        if issue.get("assignee_id") == assignee_id:
            return json.dumps({
                "success": False,
                "error": f"Issue '{issue_id}' is already assigned to user '{assignee_id}'"
            })

        # Assign the issue
        issue["assignee_id"] = assignee_id

        # Update the updated_at timestamp
        timestamp = "2026-01-01T23:59:00"
        issue["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "message": f"Issue '{issue_id}' assigned to user '{assignee_id}' successfully",
            "issue_data": issue
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:

        return {
            "type": "function",
            "function": {
                "name": "assign_issue",
                "description": "Assigns a user to an issue in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "The ID of the issue to assign.",
                        },
                        "assignee_id": {
                            "type": "string",
                            "description": "The ID of the user to assign to the issue.",
                        },
                    },
                    "required": ["issue_id", "assignee_id"],
                },
            },
        }
