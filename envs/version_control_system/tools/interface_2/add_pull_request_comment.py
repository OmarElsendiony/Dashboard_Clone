import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddPullRequestComment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        user_id: str,
        body: str,
    ) -> str:
        """Add a comment to a pull request."""
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})
        
        comments_dict = data.get("comments", {})
        pull_requests_dict = data.get("pull_requests", {})
        users_dict = data.get("users", {})
        
        pull_request_id_str = str(pull_request_id).strip()
        user_id_str = str(user_id).strip()
        body_str = str(body).strip()

        # Validate user exists
        if user_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id_str}' not found"
            })

        user = users_dict[user_id_str]
        user_status = str(user.get("status", "")).strip()

        # Validate user is active
        if user_status != "active":
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id_str}' is not active (status: {user_status})"
            })

        # Validate pull request exists
        if pull_request_id_str not in pull_requests_dict:
            return json.dumps({
                "success": False,
                "error": f"Pull request with ID '{pull_request_id_str}' not found"
            })

        new_comment_id = generate_id(comments_dict)
        new_comment = {
            "comment_id": new_comment_id,
            "commentable_type": "pull_request",
            "commentable_id": pull_request_id_str,
            "author_id": user_id_str,
            "comment_body": body_str,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        comments_dict[new_comment_id] = new_comment

        return json.dumps({
            "success": True,
            "comment": new_comment,
            "message": f"Comment added successfully to pull request '{pull_request_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the add_pull_request_comment function."""
        return {
            "type": "function",
            "function": {
                "name": "add_pull_request_comment",
                "description": "Add a comment to a pull request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The ID of the pull request to add the comment to.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user adding the comment. User must be active.",
                        },
                        "body": {
                            "type": "string",
                            "description": "The content/body of the comment.",
                        },
                    },
                    "required": ["pull_request_id", "user_id", "body"],
                },
            },
        }