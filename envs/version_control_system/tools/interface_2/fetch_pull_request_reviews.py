import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchPullRequestReviews(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        reviewer_id: Optional[str] = None,
    ) -> str:

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        pull_request_reviews_dict = data.get("pull_request_reviews", {})

        # Convert to strings
        pull_request_id_str = str(pull_request_id).strip()
        reviewer_id_str = str(reviewer_id).strip() if reviewer_id else None


        # Find matching reviews
        matching_reviews = []
        for review_id, review in pull_request_reviews_dict.items():
            if str(review.get("pull_request_id")) != pull_request_id_str:
                continue

            # Apply reviewer filter if provided
            if reviewer_id_str and str(review.get("reviewer_id")) != reviewer_id_str:
                continue

            # Add matching review
            review_copy = review.copy()
            review_copy["review_id"] = str(review_id)
            matching_reviews.append(review_copy)

        # Return results
        if not matching_reviews:
            filter_text = f"pull request '{pull_request_id_str}'"
            if reviewer_id_str:
                filter_text += f" and reviewer '{reviewer_id_str}'"
            
            return json.dumps({
                "success": False,
                "error": f"No reviews found for {filter_text}",
            })

        return json.dumps({
            "success": True,
            "pull_request_reviews": matching_reviews,
            "count": len(matching_reviews),
            "message": f"Found {len(matching_reviews)} review(s) for pull request '{pull_request_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        
        return {
            "type": "function",
            "function": {
                "name": "fetch_pull_request_reviews",
                "description": (
                    "Fetch pull request review(s) for a specific pull request. "
                    "If reviewer_id is provided, filters reviews by that reviewer. "
                    "If reviewer_id is not provided, returns all reviews for the pull request. "
                    "Returns an array of reviews with a count field indicating total matches."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The ID of the pull request to fetch reviews for.",
                        },
                        "reviewer_id": {
                            "type": "string",
                            "description": "Optional. The ID of the reviewer to filter by.",
                        },
                    },
                    "required": ["pull_request_id"],
                },
            },
        }
