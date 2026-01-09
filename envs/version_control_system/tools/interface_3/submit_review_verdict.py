import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SubmitReviewVerdict(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        reviewer_id: str,
        verdict: str,
        body: Optional[str] = None
    ) -> str:
        """
        Submits a review verdict on a pull request.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not pull_request_id:
            return json.dumps({"success": False, "error": "pull_request_id is required to submit review verdict"})
        if not reviewer_id:
            return json.dumps({"success": False, "error": "reviewer_id is required to submit review verdict"})
        if not verdict:
            return json.dumps({"success": False, "error": "verdict is required to submit review verdict"})

        # Validate verdict
        valid_verdicts = ["approved", "changes_requested", "commented", "dismissed"]
        if verdict not in valid_verdicts:
            return json.dumps({"success": False, "error": f"Invalid verdict '{verdict}'. Valid values: approved, changes_requested, commented, dismissed"})

        pull_requests = data.get("pull_requests", {})
        users = data.get("users", {})
        pull_request_reviews = data.get("pull_request_reviews", {})

        # Validate pull request exists
        if str(pull_request_id) not in pull_requests:
            return json.dumps({"success": False, "error": f"Pull request with id '{pull_request_id}' not found"})

        pull_request = pull_requests[str(pull_request_id)]

        # Validate pull request is open or draft (can't review closed/merged)
        pr_status = pull_request.get("status")
        if pr_status in ["closed", "merged"]:
            return json.dumps({"success": False, "error": f"Cannot submit review on a {pr_status} pull request"})

        # Validate reviewer exists
        if str(reviewer_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{reviewer_id}' not found"})

        # Generate new review_id
        if pull_request_reviews:
            max_review_id = max(int(k) for k in pull_request_reviews.keys())
            new_review_id = str(max_review_id + 1)
        else:
            new_review_id = "1"

        # Create pull request review record
        new_review = {
            "review_id": new_review_id,
            "pull_request_id": pull_request_id,
            "reviewer_id": reviewer_id,
            "review_state": verdict,
            "review_body": body,
            "submitted_at": "2026-01-01T23:59:00",
            "created_at": "2026-01-01T23:59:00"
        }

        pull_request_reviews[new_review_id] = new_review

        return json.dumps({"success": True, "result": new_review})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "submit_review_verdict",
                "description": "Submits a review verdict on a pull request. The reviewer provides their assessment of the changes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request to review."
                        },
                        "reviewer_id": {
                            "type": "string",
                            "description": "The unique identifier of the user submitting the review."
                        },
                        "verdict": {
                            "type": "string",
                            "description": "The review verdict. Valid values: approved, changes_requested, commented, dismissed."
                        },
                        "body": {
                            "type": "string",
                            "description": "Optional comment or explanation for the review verdict."
                        }
                    },
                    "required": ["pull_request_id", "reviewer_id", "verdict"]
                }
            }
        }
