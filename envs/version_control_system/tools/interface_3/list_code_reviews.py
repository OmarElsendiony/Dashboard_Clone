import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListCodeReviews(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        reviewer_id: str,
        status: Optional[str] = None
    ) -> str:
        """
        Lists code reviews for a pull request by a specific reviewer with optional status filter.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not pull_request_id:
            return json.dumps({"success": False, "error": "pull_request_id is required to list code reviews"})
        if not reviewer_id:
            return json.dumps({"success": False, "error": "reviewer_id is required to list code reviews"})

        # Validate status if provided
        if status is not None:
            valid_statuses = ["pending", "resolved", "outdated"]
            if status not in valid_statuses:
                return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: pending, resolved, outdated"})

        pull_requests = data.get("pull_requests", {})
        users = data.get("users", {})
        code_reviews = data.get("code_reviews", {})

        # Validate pull request exists
        if str(pull_request_id) not in pull_requests:
            return json.dumps({"success": False, "error": f"Pull request with id '{pull_request_id}' not found"})

        # Validate reviewer exists
        if str(reviewer_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{reviewer_id}' not found"})

        # Search for code reviews matching the filters
        results = []
        for code_review_id, code_review in code_reviews.items():
            # Filter by pull_request_id
            if str(code_review.get("pull_request_id")) != str(pull_request_id):
                continue

            # Filter by reviewer_id
            if str(code_review.get("reviewer_id")) != str(reviewer_id):
                continue

            # Filter by status if provided
            if status is not None and code_review.get("status") != status:
                continue

            results.append(code_review)

        return json.dumps({"success": True, "result": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_code_reviews",
                "description": "Lists code reviews for a pull request by a specific reviewer with optional status filter.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request to list code reviews for."
                        },
                        "reviewer_id": {
                            "type": "string",
                            "description": "The unique identifier of the reviewer."
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by code review status. Valid values: pending, resolved, outdated. Optional."
                        }
                    },
                    "required": ["pull_request_id", "reviewer_id"]
                }
            }
        }
