import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class RequestPrReview(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        pull_request_number: int,
        reviewer_email: str,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def find_user_by_email(users_dict: Dict[str, Any], email: str) -> tuple:
            for uid, user in users_dict.items():
                if not isinstance(user, dict):
                    continue
                if str(user.get("email", "")).strip().lower() == email.lower():
                    return str(uid), user
            return None, None

        def find_pr_by_number(
            pull_requests_dict: Dict[str, Any], repository_id_str: str, pr_number: int
        ) -> tuple:
            for pid, pr in pull_requests_dict.items():
                if not isinstance(pr, dict):
                    continue
                if (
                    str(pr.get("repository_id")) == repository_id_str
                    and pr.get("pull_request_number") == pr_number
                ):
                    return str(pid), pr
            return None, None

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'repository_id'"})

        if not pull_request_number:
            return json.dumps({"success": False, "error": "Missing required parameter: 'pull_request_number'"})

        if not reviewer_email:
            return json.dumps({"success": False, "error": "Missing required parameter: 'reviewer_email'"})

        repositories_dict = data.get("repositories", {})
        pull_requests_dict = data.get("pull_requests", {})
        pull_request_reviews_dict = data.get("pull_request_reviews", {})
        users_dict = data.get("users", {})

        repository_id_str = str(repository_id).strip()
        pr_number = int(pull_request_number)
        reviewer_email_str = str(reviewer_email).strip()

        if repository_id_str not in repositories_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with ID '{repository_id_str}' not found",
                }
            )

        repository = repositories_dict[repository_id_str]

        if not isinstance(repository, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid repository data structure for repository ID '{repository_id_str}'",
                }
            )

        pull_request_id_str, pull_request = find_pr_by_number(
            pull_requests_dict, repository_id_str, pr_number
        )

        if not pull_request_id_str or not pull_request:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Pull request #{pr_number} not found in repository '{repository_id_str}'",
                }
            )

        pr_status = str(pull_request.get("status", "")).strip()
        valid_review_statuses = ["draft", "open"]

        if pr_status not in valid_review_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Pull request #{pr_number} has status '{pr_status}' and cannot be reviewed. Only pull requests with status 'draft' or 'open' can be reviewed.",
                }
            )

        reviewer_id_str, reviewer = find_user_by_email(users_dict, reviewer_email_str)

        if not reviewer_id_str or not reviewer:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with email '{reviewer_email_str}' not found",
                }
            )

        reviewer_status = reviewer.get("status")
        if reviewer_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"User '{reviewer_email_str}' is not active and cannot review pull requests",
                }
            )

        pr_author_id = str(pull_request.get("author_id", "")).strip()
        if reviewer_id_str == pr_author_id:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Pull request author cannot review their own pull request",
                }
            )

        for _, review in pull_request_reviews_dict.items():
            if not isinstance(review, dict):
                continue
            if (
                review.get("pull_request_id") == pull_request_id_str
                and review.get("reviewer_id") == reviewer_id_str
            ):
                existing_status = str(review.get("review_status", "")).strip()
                if existing_status == "pending":
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Reviewer '{reviewer_email_str}' already has a pending review for pull request #{pr_number}",
                        }
                    )

        new_review_id = generate_id(pull_request_reviews_dict)
        new_review = {
            "review_id": str(new_review_id) if new_review_id else None,
            "pull_request_id": str(pull_request_id_str) if pull_request_id_str else None,
            "reviewer_id": str(reviewer_id_str) if reviewer_id_str else None,
            "review_status": "pending",
            "review_comment": None,
            "submitted_at": None,
            "created_at": timestamp,
        }
        pull_request_reviews_dict[new_review_id] = new_review

        pull_request["updated_at"] = timestamp

        review_return = new_review.copy()
        review_return["reviewer_email"] = reviewer.get("email")
        review_return["reviewer_name"] = (
            f"{reviewer.get('first_name', '')} {reviewer.get('last_name', '')}".strip()
        )
        review_return["pull_request_title"] = pull_request.get("title")
        review_return["pull_request_number"] = pr_number
        review_return["repository_name"] = repository.get("repository_name")

        message = f"Review requested from '{reviewer_email_str}' for pull request #{pr_number}: '{pull_request.get('title', '')}'"

        return json.dumps(
            {
                "success": True,
                "review": review_return,
                "message": message,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "request_pr_review",
                "description": (
                    "Requests a code review from a specified reviewer for a pull request. "
                    "This function initiates the review process by assigning a reviewer to evaluate proposed code changes. "
                    "Use this when a pull request is ready for technical evaluation, when security-related changes require approval from security specialists, "
                    "or when critical fixes need validation before merging. "
                    "The reviewer will be notified and can approve, request changes, or reject the pull request."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository containing the pull request.",
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "The pull request number requiring review.",
                        },
                        "reviewer_email": {
                            "type": "string",
                            "description": "The email address of the user being requested to review the pull request.",
                        },
                    },
                    "required": [
                        "repository_id",
                        "pull_request_number",
                        "reviewer_email",
                    ],
                },
            },
        }
