import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateComment(Tool):
    """Tool for creating a comment on an issue or pull request in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        reference_type: str,
        reference_id: str,
        actor_id: str,
        body: str,
    ) -> str:
        """
        Create a new comment on an issue or pull request.

        Args:
            data: The data dictionary containing all version control system data.
            reference_type: The type of reference to comment on (issue/pull_request). Required.
            reference_id: The ID of the issue or pull request to comment on. Required.
            actor_id: The ID of the user creating the comment. Required.
            body: The content of the comment. Required.

        Returns:
            str: A JSON-encoded string containing the success status and created comment data.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """
            Generates a new unique ID for a record.

            Returns:
                str: The new unique ID as a string.
            """
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        comments = data.get("comments", {})
        users = data.get("users", {})
        issues = data.get("issues", {})
        pull_requests = data.get("pull_requests", {})

        # Validate required fields
        if not reference_type:
            return json.dumps({"success": False, "error": "Missing required parameter: reference_type"})

        if not reference_id:
            return json.dumps({"success": False, "error": "Missing required parameter: reference_id"})

        if not actor_id:
            return json.dumps({"success": False, "error": "Missing required parameter: actor_id"})

        if not body:
            return json.dumps({"success": False, "error": "Missing required parameter: body"})

        if not isinstance(body, str) or not body.strip():
            return json.dumps({"success": False, "error": "body must be a non-empty string"})

        # Validate reference_type
        reference_type = reference_type.strip().lower() if isinstance(reference_type, str) else ""
        allowed_reference_types = {"issue", "pull_request"}
        if reference_type not in allowed_reference_types:
            return json.dumps({
                "success": False,
                "error": f"reference_type must be one of: {', '.join(sorted(allowed_reference_types))}"
            })

        # Validate author exists and is active
        actor_id = str(actor_id)
        if actor_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{actor_id}' not found"
            })

        author = users[actor_id]

        if author.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{actor_id}' is not active"
            })

        # Validate reference exists
        reference_id = str(reference_id)

        if reference_type == "issue":
            if reference_id not in issues:
                return json.dumps({
                    "success": False,
                    "error": f"Issue with ID '{reference_id}' not found"
                })

            issue = issues[reference_id]

            # Check if issue is closed
            if issue.get("status") == "closed":
                return json.dumps({
                    "success": False,
                    "error": f"Cannot comment on closed issue '{reference_id}'"
                })

            # Map reference_type to commentable_type format used in data
            commentable_type = "issue"

        elif reference_type == "pull_request":
            if reference_id not in pull_requests:
                return json.dumps({
                    "success": False,
                    "error": f"Pull request with ID '{reference_id}' not found"
                })

            pull_request = pull_requests[reference_id]

            # Check if pull request is closed or merged
            pr_status = pull_request.get("status")
            if pr_status in ("closed", "merged"):
                return json.dumps({
                    "success": False,
                    "error": f"Cannot comment on {pr_status} pull request '{reference_id}'"
                })

            # Map reference_type to commentable_type format used in data
            commentable_type = "pull_request"

        # Generate new comment ID
        new_comment_id = generate_id(comments)

        # Set timestamp for created_at and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Create new comment record
        new_comment = {
            "comment_id": new_comment_id,
            "commentable_type": commentable_type,
            "commentable_id": reference_id,
            "author_id": actor_id,
            "comment_body": body.strip(),
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add the new comment to the comments dictionary
        comments[new_comment_id] = new_comment

        return json.dumps({
            "success": True,
            "message": f"Comment created successfully on {reference_type} '{reference_id}'",
            "comment_id": new_comment_id,
            "comment_data": new_comment
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the create_comment function."""
        return {
            "type": "function",
            "function": {
                "name": "create_comment",
                "description": "Creates a new comment on an issue or pull request in the version control system. The comment will be associated with the specified reference and authored by the given user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reference_type": {
                            "type": "string",
                            "description": "The type of reference to comment on (issue or pull_request).",
                        },
                        "reference_id": {
                            "type": "string",
                            "description": "The ID of the issue or pull request.",
                        },
                        "actor_id": {
                            "type": "string",
                            "description": "The ID of the user creating the comment.",
                        },
                        "body": {
                            "type": "string",
                            "description": "The content of the comment.",
                        },
                    },
                    "required": ["reference_type", "reference_id", "actor_id", "body"],
                },
            },
        }
