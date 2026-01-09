import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetIssue(Tool):
    """Tool for retrieving issue details from the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        issue_number: int,
    ) -> str:
        """
        Retrieve issue details by repository ID and issue number.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository containing the issue (required).
            issue_number: The issue number within the repository (required).

        Returns:
            JSON string containing the success status and issue data if found.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        issues = data.get("issues", {})
        comments = data.get("comments", {})
        labels = data.get("labels", {})

        # Convert repo_id to string for consistent comparison
        repo_id = str(repo_id)
        issue_number = int(issue_number)

        # Search for issue by repository_id and issue_number
        found_issue = None
        for _, issue in issues.items():
            if (
                str(issue.get("repository_id")) == repo_id
                and issue.get("issue_number") == issue_number
            ):
                found_issue = issue.copy()
                break

        if not found_issue:
            return json.dumps({
                "success": False,
                "error": f"Issue with number '{issue_number}' not found in repository '{repo_id}'"
            })

        issue_id = found_issue.get("issue_id")

        # Include comments made on the issue
        issue_comments = []
        for _, comment in comments.items():
            if (
                comment.get("commentable_type") == "issue"
                and str(comment.get("commentable_id")) == str(issue_id)
            ):
                issue_comments.append({
                    "comment_id": comment.get("comment_id"),
                    "author_id": comment.get("author_id"),
                    "comment_body": comment.get("comment_body"),
                    "created_at": comment.get("created_at"),
                    "updated_at": comment.get("updated_at"),
                })
        # Sort comments by created_at
        issue_comments.sort(key=lambda x: x.get("created_at", ""))
        found_issue["comments"] = issue_comments

        # Find labels associated with this issue
        issue_labels = []
        for _, label in labels.items():
            if str(label.get("repository_id")) == repo_id:
                issue_ids_str = label.get("issue_ids")
                if issue_ids_str:
                    try:
                        issue_ids_list = json.loads(issue_ids_str)
                        if str(issue_id) in issue_ids_list:
                            issue_labels.append({
                                "label_id": label.get("label_id"),
                                "label_name": label.get("label_name"),
                                "color": label.get("color"),
                                "description": label.get("description"),
                            })
                    except json.JSONDecodeError:
                        pass

        found_issue["labels"] = issue_labels

        return json.dumps({
            "success": True,
            "issue_data": found_issue
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the get_issue function."""
        return {
            "type": "function",
            "function": {
                "name": "get_issue",
                "description": "Retrieves detailed information about an issue from a repository, including the issue details, associated labels, and comments made on the issue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the issue.",
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "The issue number within the repository.",
                        },
                    },
                    "required": ["repo_id", "issue_number"],
                },
            },
        }
