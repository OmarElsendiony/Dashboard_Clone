import json
from typing import Dict, Optional, Any
from tau_bench.envs.tool import Tool


class SubmitPullRequestReview(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        reviewer_id: str,
        review_status: str,
        pull_request_number: Optional[int] = None,
        pull_request_id: Optional[str] = None,
        review_comment: Optional[str] = None,
    ) -> str:
        pull_requests = data.get("pull_requests", {})
        pull_request_reviews = data.get("pull_request_reviews", {})
        users = data.get("users", {})
        timestamp = "2026-02-02 23:59:00"

        if not reviewer_id:
            return json.dumps({"error": "reviewer_id is required"})

        if not review_status:
            return json.dumps({"error": "review_status is required"})

        valid_statuses = ("approved", "changes_requested", "rejected")
        if review_status not in valid_statuses:
            return json.dumps(
                {"error": f"Invalid review_status '{review_status}'. Must be one of: {', '.join(valid_statuses)}"}
            )

        if pull_request_number is None and pull_request_id is None:
            return json.dumps(
                {"error": "Either pull_request_number or pull_request_id must be provided"}
            )

        reviewer = users.get(str(reviewer_id))
        if not reviewer:
            return json.dumps({"error": f"Reviewer with ID '{reviewer_id}' not found"})

        pr = None

        if pull_request_number is not None and pull_request_id is not None:
            pr = pull_requests.get(str(pull_request_id))
            if not pr:
                return json.dumps(
                    {"error": f"Pull request with ID '{pull_request_id}' not found"}
                )
            if pr.get("pull_request_number") != int(pull_request_number):
                return json.dumps(
                    {"error": f"Mismatch: pull_request_id '{pull_request_id}' does not correspond to pull_request_number {int(pull_request_number)}"}
                )

        elif pull_request_id is not None:
            pr = pull_requests.get(str(pull_request_id))
            if not pr:
                return json.dumps(
                    {"error": f"Pull request with ID '{pull_request_id}' not found"}
                )

        else:
            pull_request_number = int(pull_request_number)
            for p in pull_requests.values():
                if p.get("pull_request_number") == pull_request_number:
                    pr = p
                    break
            if not pr:
                return json.dumps(
                    {"error": f"Pull request with number {pull_request_number} not found"}
                )

        pr_status = pr.get("status")
        if pr_status not in ("open", "draft"):
            return json.dumps(
                {"error": f"Pull request cannot be reviewed. Current status is '{pr_status}'. Only pull requests with status 'open' or 'draft' can be reviewed"}
            )

        if not pull_request_reviews:
            new_id = "1"
        else:
            new_id = str(max(int(k) for k in pull_request_reviews.keys()) + 1)

        new_review = {
            "review_id": new_id,
            "pull_request_id": str(pr["pull_request_id"]),
            "reviewer_id": str(reviewer_id),
            "review_status": str(review_status),
            "review_comment": str(review_comment) if review_comment else "",
            "submitted_at": timestamp,
            "created_at": timestamp,
        }

        pull_request_reviews[new_id] = new_review

        return json.dumps({
            "success": True,
            "review": {
                "review_id": str(new_review["review_id"]),
                "pull_request_id": str(new_review["pull_request_id"]),
                "reviewer_id": str(new_review["reviewer_id"]),
                "review_status": str(new_review["review_status"]),
                "review_comment": str(new_review["review_comment"]),
                "submitted_at": str(new_review["submitted_at"]),
                "created_at": str(new_review["created_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "submit_pull_request_review",
                "description": "Submits a review on a pull request with an approval, change request, or rejection decision. This tool should be used when a user wants to provide feedback on a pull request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reviewer_id": {
                            "type": "string",
                            "description": "The ID of the user submitting the review",
                        },
                        "review_status": {
                            "type": "string",
                            "description": "The review decision for the pull request",
                            "enum": ["approved", "changes_requested", "rejected"],
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "The number of the pull request",
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request",
                        },
                        "review_comment": {
                            "type": "string",
                            "description": "The comment to include with the review",
                        },
                    },
                    "required": ["reviewer_id", "review_status"],
                    "oneOf": [
                        {"required": ["pull_request_number"]},
                        {"required": ["pull_request_id"]},
                    ],
                },
            },
        }
