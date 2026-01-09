import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SubmitPullRequestReview(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        pull_request_review_id: Optional[str] = None,
        user_id: Optional[str] = None,
        review_state: Optional[str] = None,
        review_body: Optional[str] = None,
    ) -> str:
        """Submit or update a pull request review."""
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        pull_request_reviews_dict = data.get("pull_request_reviews", {})

        pull_request_id_str = str(pull_request_id).strip()
        pull_request_review_id_str = str(pull_request_review_id).strip() if pull_request_review_id else None
        user_id_str = str(user_id).strip() if user_id else None
        review_state_str = str(review_state).strip() if review_state else None
        review_body_str = str(review_body).strip() if review_body else None

        valid_states = ["pending", "approved", "changes_requested", "commented", "dismissed"]
        if review_state_str and review_state_str not in valid_states:
            return json.dumps({
                "success": False,
                "error": f"Invalid review_state '{review_state_str}'. Must be one of: {', '.join(valid_states)}",
            })        

        # Handle update scenario (pull_request_review_id provided)
        if pull_request_review_id_str:
            review = pull_request_reviews_dict[pull_request_review_id_str]

            # Validate review_state if provided
            if review_state_str:
                review["review_state"] = review_state_str
                review["submitted_at"] = timestamp

            # Update review_body if provided
            if review_body_str is not None:
                review["review_body"] = review_body_str

            review["created_at"] = review.get("created_at", timestamp)
            
            review_return = review.copy()
            review_return["review_id"] = pull_request_review_id_str

            return json.dumps({
                "success": True,
                "pull_request_review": review_return,
                "message": f"Pull request review '{pull_request_review_id_str}' updated successfully",
            })

        if not user_id_str or not review_state_str or review_body_str is None:
            return json.dumps({
                "success": False,
                "error": "user_id, review_state, and review_body are required when creating a new review",
            })


        # Create new review
        new_review_id = generate_id(pull_request_reviews_dict)
        new_review = {
            "review_id": new_review_id,
            "pull_request_id": pull_request_id_str,
            "reviewer_id": user_id_str,
            "review_state": str(review_state_str),
            "review_body": review_body_str,
            "submitted_at": timestamp,
            "created_at": timestamp,
        }

        pull_request_reviews_dict[new_review_id] = new_review

        return json.dumps({
            "success": True,
            "pull_request_review": new_review,
            "message": f"Pull request review created successfully with ID '{new_review_id}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the submit_pull_request_reviews function."""
        return {
            "type": "function",
            "function": {
                "name": "submit_pull_request_review",
                "description": (
                    "Submit a new pull request review or update an existing one. "
                    "If pull_request_review_id is NOT provided: Creates a new review. "
                    "Requires user_id, review_state, and review_body. "
                    "If pull_request_review_id IS provided: Updates an existing review and user_id is ignored. "
                    "Only review_state and/or review_body can be updated. "
                    "Valid review_state values: pending, approved, changes_requested, commented, dismissed. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The ID of the pull request.",
                        },
                        "pull_request_review_id": {
                            "type": "string",
                            "description": "Optional. The ID of the review to update. If not provided, a new review is created.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Optional. The ID of the user submitting the review. Required when creating a new review, ignored when updating.",
                        },
                        "review_state": {
                            "type": "string",
                            "description": "Optional. Valid values: pending, approved, changes_requested, commented, dismissed. Required for new reviews.",
                        },
                        "review_body": {
                            "type": "string",
                            "description": "Optional. The body/content of the review. Required for new reviews.",
                        },
                    },
                    "required": ["pull_request_id"],
                },
            },
        }
