import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class PostComment(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        commentable_type: str,
        author_id: str,
        comment_body: str,
        issue_id: Optional[str] = None,
        pull_request_id: Optional[str] = None
    ) -> str:
        """
        Posts a comment on an issue or pull request.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not commentable_type:
            return json.dumps({"success": False, "error": "commentable_type is required to post a comment"})
        if not author_id:
            return json.dumps({"success": False, "error": "author_id is required to post a comment"})
        if not comment_body:
            return json.dumps({"success": False, "error": "comment_body is required to post a comment"})

        # Validate commentable_type
        valid_commentable_types = ["issue", "pull_request"]
        if commentable_type not in valid_commentable_types:
            return json.dumps({"success": False, "error": f"Invalid commentable_type '{commentable_type}'. Valid values: issue, pull_request"})

        # Validate appropriate ID is provided based on commentable_type
        if commentable_type == "issue":
            if not issue_id:
                return json.dumps({"success": False, "error": "issue_id is required when commentable_type is 'issue'"})
            commentable_id = issue_id
        else:  # pull_request
            if not pull_request_id:
                return json.dumps({"success": False, "error": "pull_request_id is required when commentable_type is 'pull_request'"})
            commentable_id = pull_request_id

        users = data.get("users", {})
        issues = data.get("issues", {})
        pull_requests = data.get("pull_requests", {})
        comments = data.get("comments", {})

        # Validate author exists
        if str(author_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{author_id}' not found"})

        # Validate commentable entity exists
        if commentable_type == "issue":
            if str(issue_id) not in issues:
                return json.dumps({"success": False, "error": f"Issue with id '{issue_id}' not found"})
        else:  # pull_request
            if str(pull_request_id) not in pull_requests:
                return json.dumps({"success": False, "error": f"Pull request with id '{pull_request_id}' not found"})

        # Generate new comment_id
        if comments:
            max_id = max(int(k) for k in comments.keys())
            new_comment_id = str(max_id + 1)
        else:
            new_comment_id = "1"

        # Create comment record
        new_comment = {
            "comment_id": new_comment_id,
            "commentable_type": commentable_type,
            "commentable_id": commentable_id,
            "author_id": author_id,
            "comment_body": comment_body,
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00"
        }

        comments[new_comment_id] = new_comment

        return json.dumps({"success": True, "result": new_comment})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "post_comment",
                "description": "Posts a comment on an issue or pull request. Specify the commentable_type and provide the corresponding issue_id or pull_request_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commentable_type": {
                            "type": "string",
                            "description": "The type of entity to comment on. Valid values: issue, pull_request."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user posting the comment."
                        },
                        "comment_body": {
                            "type": "string",
                            "description": "The content of the comment."
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "The unique identifier of the issue to comment on. Required when commentable_type is 'issue'."
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request to comment on. Required when commentable_type is 'pull_request'."
                        }
                    },
                    "required": ["commentable_type", "author_id", "comment_body"]
                }
            }
        }
