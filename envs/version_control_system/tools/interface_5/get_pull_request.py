import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetPullRequest(Tool):
    """Tool for retrieving pull request details from the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        pull_request_number: int,
        include_reviews: Optional[bool] = False,
        include_comments: Optional[bool] = False,
    ) -> str:
        """
        Retrieve pull request details by repository ID and pull request number.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository containing the pull request (required).
            pull_request_number: The pull request number within the repository (required).
            include_reviews: Whether to include reviews in the response (optional, default False).
            include_comments: Whether to include comments in the response (optional, default False).

        Returns:
            JSON string containing the success status and pull request data if found.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        pull_requests = data.get("pull_requests", {})
        pull_request_reviews = data.get("pull_request_reviews", {})
        comments = data.get("comments", {})

        # Convert repo_id to string for consistent comparison
        repo_id = str(repo_id)
        pull_request_number = int(pull_request_number)

        # Search for pull request by repository_id and pull_request_number
        found_pr = None
        for _, pr in pull_requests.items():
            if (
                str(pr.get("repository_id")) == repo_id
                and pr.get("pull_request_number") == pull_request_number
            ):
                found_pr = pr.copy()
                break

        if not found_pr:
            return json.dumps({
                "success": False,
                "error": f"Pull request with number '{pull_request_number}' not found in repository '{repo_id}'"
            })

        pull_request_id = found_pr.get("pull_request_id")

        # Build the response with all relevant pull request information
        pr_data = {
            "pull_request_id": found_pr.get("pull_request_id"),
            "repository_id": found_pr.get("repository_id"),
            "pull_request_number": found_pr.get("pull_request_number"),
            "title": found_pr.get("title"),
            "description": found_pr.get("description"),
            "author_id": found_pr.get("author_id"),
            "source_branch": found_pr.get("source_branch"),
            "target_branch": found_pr.get("target_branch"),
            "status": found_pr.get("status"),
            "merged_by": found_pr.get("merged_by"),
            "merged_at": found_pr.get("merged_at"),
            "closed_at": found_pr.get("closed_at"),
            "created_at": found_pr.get("created_at"),
            "updated_at": found_pr.get("updated_at"),
        }

        # Include reviews if requested
        if include_reviews:
            pr_reviews = []
            for _, review in pull_request_reviews.items():
                if str(review.get("pull_request_id")) == str(pull_request_id):
                    pr_reviews.append({
                        "review_id": review.get("review_id"),
                        "pull_request_id": review.get("pull_request_id"),
                        "reviewer_id": review.get("reviewer_id"),
                        "review_state": review.get("review_state"),
                        "review_body": review.get("review_body"),
                        "submitted_at": review.get("submitted_at"),
                        "created_at": review.get("created_at"),
                    })
            # Sort reviews by created_at
            pr_reviews.sort(key=lambda x: x.get("created_at", ""))
            pr_data["reviews"] = pr_reviews

        # Include comments if requested
        if include_comments:
            pr_comments = []
            for _, comment in comments.items():
                if (
                    comment.get("commentable_type") == "pull_request"
                    and str(comment.get("commentable_id")) == str(pull_request_id)
                ):
                    pr_comments.append({
                        "comment_id": comment.get("comment_id"),
                        "author_id": comment.get("author_id"),
                        "comment_body": comment.get("comment_body"),
                        "created_at": comment.get("created_at"),
                        "updated_at": comment.get("updated_at"),
                    })
            # Sort comments by created_at
            pr_comments.sort(key=lambda x: x.get("created_at", ""))
            pr_data["comments"] = pr_comments

        return json.dumps({
            "success": True,
            "pull_request_data": pr_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the get_pull_request function."""
        return {
            "type": "function",
            "function": {
                "name": "get_pull_request",
                "description": "Retrieve detailed information about a specific pull request. Optionally includes associated reviews and comments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the pull request.",
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "The pull request number within the repository.",
                        },
                        "include_reviews": {
                            "type": "boolean",
                            "description": "Whether to include reviews in the response. Optional, defaults to false.",
                        },
                        "include_comments": {
                            "type": "boolean",
                            "description": "Whether to include comments in the response. Optional, defaults to false.",
                        },
                    },
                    "required": ["repo_id", "pull_request_number"],
                },
            },
        }
