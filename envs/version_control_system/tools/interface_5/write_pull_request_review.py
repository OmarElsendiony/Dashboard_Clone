import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class WritePullRequestReview(Tool):
    """Tool for requesting or submitting pull request reviews in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        pull_request_id: str,
        reviewer_id: Optional[str] = None,
        review_id: Optional[str] = None,
        review_state: Optional[str] = None,
        body: Optional[str] = None,
    ) -> str:
        """
        Request a review from a user or submit an existing pending review.

        Args:
            data: The data dictionary containing all version control system data.
            action: The action to perform. Must be one of: "request" (request a review), "submit" (submit a review).
            pull_request_id: The ID of the pull request (required).
            reviewer_id: The ID of the user to request a review from. Required for "request" action.
            review_id: The ID of the existing pending review to submit. Required for "submit" action.
            review_state: The state of the review. Must be one of: approved, changes_requested.
                          Required for "submit" action.
            body: The body/comment of the review. Optional for "submit" action.

        Returns:
            JSON string containing the success status and review data.
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

        pull_requests = data.get("pull_requests", {})
        pull_request_reviews = data.get("pull_request_reviews", {})
        users = data.get("users", {})

        # Validate action
        if not action or not isinstance(action, str):
            return json.dumps({"success": False, "error": "action is required and must be a string"})
        action = action.strip().lower()

        allowed_actions = {"request", "submit"}
        if action not in allowed_actions:
            return json.dumps({
                "success": False,
                "error": f"action must be one of: {', '.join(sorted(allowed_actions))}"
            })

        # Validate pull_request_id
        if not pull_request_id or not str(pull_request_id).strip():
            return json.dumps({"success": False, "error": "pull_request_id must be provided"})
        pull_request_id = str(pull_request_id).strip()

        # Find the pull request
        found_pr = None
        for _, pr in pull_requests.items():
            if str(pr.get("pull_request_id")) == pull_request_id:
                found_pr = pr
                break

        if not found_pr:
            return json.dumps({
                "success": False,
                "error": f"Pull request with ID '{pull_request_id}' not found"
            })

        # Check if pull request is already closed or merged
        pr_status = found_pr.get("status", "").lower()
        if pr_status in {"closed", "merged"}:
            return json.dumps({
                "success": False,
                "error": f"Cannot perform review action on pull request '{pull_request_id}': it is already {pr_status}"
            })

        timestamp = "2026-01-01T23:59:00"

        if action == "request":
            # Validate reviewer_id is required for request action
            if not reviewer_id or not str(reviewer_id).strip():
                return json.dumps({
                    "success": False,
                    "error": "reviewer_id is required for 'request' action"
                })
            reviewer_id = str(reviewer_id).strip()

            # Check if reviewer user exists
            reviewer = None
            for _, u in users.items():
                if str(u.get("user_id")) == reviewer_id:
                    reviewer = u
                    break

            if not reviewer:
                return json.dumps({
                    "success": False,
                    "error": f"User with ID '{reviewer_id}' not found"
                })

            # Check if reviewer is active
            if reviewer.get("status") != "active":
                return json.dumps({
                    "success": False,
                    "error": f"User '{reviewer_id}' is not active"
                })

            # Check if a pending review already exists for this reviewer on this PR
            for _, review in pull_request_reviews.items():
                if (
                    str(review.get("pull_request_id")) == pull_request_id
                    and str(review.get("reviewer_id")) == reviewer_id
                    and review.get("review_state") == "pending"
                ):
                    return json.dumps({
                        "success": False,
                        "error": f"A pending review request already exists for user '{reviewer_id}' on pull request '{pull_request_id}'"
                    })

            # Create new pending review request
            new_review_id = generate_id(pull_request_reviews)

            new_review = {
                "review_id": new_review_id,
                "pull_request_id": pull_request_id,
                "reviewer_id": reviewer_id,
                "review_state": "pending",
                "review_body": "",
                "submitted_at": None,
                "created_at": timestamp,
            }

            pull_request_reviews[new_review_id] = new_review

            return json.dumps({
                "success": True,
                "message": f"Review request created successfully for user '{reviewer_id}' on pull request '{pull_request_id}'",
                "action_performed": "requested",
                "review_data": new_review
            })

        elif action == "submit":
            # Validate review_id is required for submit action
            if not review_id or not str(review_id).strip():
                return json.dumps({
                    "success": False,
                    "error": "review_id is required for 'submit' action"
                })
            review_id = str(review_id).strip()

            # Validate review_state is required for submit action
            if not review_state or not isinstance(review_state, str) or not review_state.strip():
                return json.dumps({
                    "success": False,
                    "error": "review_state is required for 'submit' action"
                })
            review_state = review_state.strip().lower()

            allowed_review_states = {"approved", "changes_requested"}
            if review_state not in allowed_review_states:
                return json.dumps({
                    "success": False,
                    "error": f"review_state must be one of: {', '.join(sorted(allowed_review_states))}"
                })

            # Find the existing review
            existing_review = None
            for key, review in pull_request_reviews.items():
                if str(review.get("review_id")) == review_id:
                    existing_review = review
                    break

            if not existing_review:
                return json.dumps({
                    "success": False,
                    "error": f"Review with ID '{review_id}' not found"
                })

            # Check that the review is for the specified pull request
            if str(existing_review.get("pull_request_id")) != pull_request_id:
                return json.dumps({
                    "success": False,
                    "error": f"Review '{review_id}' does not belong to pull request '{pull_request_id}'"
                })

            # Check that the review is in pending state
            current_review_state = existing_review.get("review_state", "")
            if current_review_state != "pending":
                return json.dumps({
                    "success": False,
                    "error": f"Review '{review_id}' is not in pending state (current state: {current_review_state})"
                })

            # Update the review
            existing_review["review_state"] = review_state
            existing_review["submitted_at"] = timestamp

            # Update body if provided
            if body is not None:
                if isinstance(body, str):
                    existing_review["review_body"] = body.strip()
                else:
                    return json.dumps({
                        "success": False,
                        "error": "body must be a string"
                    })

            return json.dumps({
                "success": True,
                "message": f"Review '{review_id}' submitted successfully with state '{review_state}'",
                "action_performed": "submitted",
                "review_data": existing_review
            })

        # Should not reach here due to action validation above
        return json.dumps({"success": False, "error": "Unknown error occurred"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the write_pull_request_review function."""
        return {
            "type": "function",
            "function": {
                "name": "write_pull_request_review",
                "description": "Request a review from a user or submit an existing review on a pull request. Use action='request' to request a review from a specific user. Use action='submit' to submit a review with a state and optional body text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform. Must be one of: 'request' (request a review from a user), 'submit' (submit a review).",
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "The ID of the pull request.",
                        },
                        "reviewer_id": {
                            "type": "string",
                            "description": "The ID of the user to request a review from. Required for 'request' action.",
                        },
                        "review_id": {
                            "type": "string",
                            "description": "The ID of the review to submit. Required for 'submit' action.",
                        },
                        "review_state": {
                            "type": "string",
                            "description": "The state of the review. Must be one of: 'approved', 'changes_requested'. Required for 'submit' action.",
                        },
                        "body": {
                            "type": "string",
                            "description": "The body/comment of the review. Optional for 'submit' action.",
                        },
                    },
                    "required": ["action", "pull_request_id"],
                },
            },
        }
