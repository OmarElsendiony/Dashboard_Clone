import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AttachDetachIssueLabels(Tool):
    """Tool for attaching or detaching labels on issues in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        label_id: str,
        issue_id: str,
    ) -> str:
        """
        Attach or detach a label from an issue.

        Args:
            data: The data dictionary containing all version control system data.
            action: The action to perform. Must be either 'attach_to_issue' or 'detach_from_issue' (required).
            label_id: The ID of the label to attach or detach (required).
            issue_id: The ID of the issue to attach the label to or detach from (required).

        Returns:
            str: A JSON-encoded string containing the success status and updated label data.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        labels = data.get("labels", {})
        issues = data.get("issues", {})
        repositories = data.get("repositories", {})

        # Validate action
        if not action:
            return json.dumps({"success": False, "error": "Missing required parameter: action"})

        if not isinstance(action, str):
            return json.dumps({"success": False, "error": "action must be a string"})

        action = action.strip().lower()
        allowed_actions = {"attach_to_issue", "detach_from_issue"}
        if action not in allowed_actions:
            return json.dumps({
                "success": False,
                "error": f"action must be one of: {', '.join(sorted(allowed_actions))}"
            })

        # Validate label_id
        if not label_id:
            return json.dumps({"success": False, "error": "Missing required parameter: label_id"})

        if not isinstance(label_id, str):
            return json.dumps({"success": False, "error": "label_id must be a string"})

        label_id = str(label_id).strip()

        if not label_id:
            return json.dumps({"success": False, "error": "label_id cannot be empty"})

        # Validate issue_id
        if not issue_id:
            return json.dumps({"success": False, "error": "Missing required parameter: issue_id"})

        if not isinstance(issue_id, str):
            return json.dumps({"success": False, "error": "issue_id must be a string"})

        issue_id = str(issue_id).strip()

        if not issue_id:
            return json.dumps({"success": False, "error": "issue_id cannot be empty"})

        # Check if label exists
        if label_id not in labels:
            return json.dumps({
                "success": False,
                "error": f"Label with ID '{label_id}' not found"
            })

        label = labels[label_id]

        # Check if issue exists
        if issue_id not in issues:
            return json.dumps({
                "success": False,
                "error": f"Issue with ID '{issue_id}' not found"
            })

        issue = issues[issue_id]

        # Verify that the label and issue belong to the same repository
        label_repo_id = str(label.get("repository_id"))
        issue_repo_id = str(issue.get("repository_id"))

        if label_repo_id != issue_repo_id:
            return json.dumps({
                "success": False,
                "error": f"Label '{label_id}' and issue '{issue_id}' belong to different repositories"
            })

        # Check if repository is archived
        if label_repo_id in repositories:
            repository = repositories[label_repo_id]
            if repository.get("is_archived", False):
                return json.dumps({
                    "success": False,
                    "error": f"Cannot modify labels in archived repository '{label_repo_id}'"
                })

        # Parse issue_ids from the label (stored as JSON string or None)
        issue_ids_str = label.get("issue_ids")
        issue_ids_list = []
        if issue_ids_str:
            try:
                issue_ids_list = json.loads(issue_ids_str)
            except json.JSONDecodeError:
                issue_ids_list = []

        # Ensure issue_ids_list is a list
        if not isinstance(issue_ids_list, list):
            issue_ids_list = []

        if action == "attach_to_issue":
            # Check if the label is already attached to the issue
            if issue_id in issue_ids_list:
                return json.dumps({
                    "success": False,
                    "error": f"Label '{label_id}' is already attached to issue '{issue_id}'"
                })

            # Attach the label to the issue
            issue_ids_list.append(issue_id)
            label["issue_ids"] = json.dumps(issue_ids_list)

            message = f"Label '{label_id}' attached to issue '{issue_id}' successfully"

        elif action == "detach_from_issue":
            # Check if the label is attached to the issue
            if issue_id not in issue_ids_list:
                return json.dumps({
                    "success": False,
                    "error": f"Label '{label_id}' is not attached to issue '{issue_id}'"
                })

            # Detach the label from the issue
            issue_ids_list.remove(issue_id)

            # Set to null if empty, otherwise save as JSON string
            if issue_ids_list:
                label["issue_ids"] = json.dumps(issue_ids_list)
            else:
                label["issue_ids"] = None

            message = f"Label '{label_id}' detached from issue '{issue_id}' successfully"

        # Parse pr_ids for response (stored as JSON string or None)
        pr_ids_str = label.get("pr_ids")
        pr_ids_list = []
        if pr_ids_str:
            try:
                pr_ids_list = json.loads(pr_ids_str)
            except json.JSONDecodeError:
                pr_ids_list = []

        # Build response with parsed data (matching get_label response format)
        label_data = {
            "label_id": label.get("label_id"),
            "repository_id": label.get("repository_id"),
            "label_name": label.get("label_name"),
            "color": label.get("color"),
            "description": label.get("description"),
            "issue_ids": issue_ids_list,
            "pr_ids": pr_ids_list,
            "created_at": label.get("created_at"),
        }

        return json.dumps({
            "success": True,
            "message": message,
            "label_data": label_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the attach_detach_issue_labels function."""
        return {
            "type": "function",
            "function": {
                "name": "attach_detach_issue_labels",
                "description": "Attaches or detaches a label from an issue in a repository. Use action='attach_to_issue' to attach a label to an issue, or action='detach_from_issue' to remove a label from an issue. Both the label and issue must exist and belong to the same repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform: 'attach_to_issue' or 'detach_from_issue'.",
                        },
                        "label_id": {
                            "type": "string",
                            "description": "The ID of the label.",
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "The ID of the issue.",
                        },
                    },
                    "required": ["action", "label_id", "issue_id"],
                },
            },
        }
