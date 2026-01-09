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

        pull_request_id_str = str(pull_request_id).strip()
        user_id_str = str(user_id).strip()
        body_str = str(body).strip()

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
                "description": (
                    "Add a comment to a pull request. "
                    "Creates a new comment entry in the comments table with commentable_type set to 'pull_request'. "
                    "Returns the created comment details including the auto-generated comment_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The ID of the pull request to add the comment to.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user adding the comment.",
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
