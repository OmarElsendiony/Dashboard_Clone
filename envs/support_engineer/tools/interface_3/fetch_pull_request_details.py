import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchPullRequestDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
        pull_request_number: Optional[int] = None,
        pull_request_id: Optional[str] = None,
    ) -> str:
        repositories = data.get("repositories", {})
        pull_requests = data.get("pull_requests", {})
        pull_request_reviews = data.get("pull_request_reviews", {})

        if not repository_name:
            return json.dumps({"error": "repository_name is required"})

        repository_id = None
        for repo in repositories.values():
            if repo.get("repository_name") == str(repository_name):
                repository_id = str(repo.get("repository_id"))
                break

        if not repository_id:
            return json.dumps({"error": f"Repository '{repository_name}' not found"})

        if pull_request_number is None and pull_request_id is None:
            return json.dumps(
                {"error": "Either pull_request_number or pull_request_id must be provided"}
            )

        def build_review_response(review):
            return {
                "review_id": str(review["review_id"]),
                "pull_request_id": str(review["pull_request_id"]),
                "reviewer_id": str(review["reviewer_id"]),
                "review_status": str(review["review_status"]),
                "review_comment": str(review["review_comment"]) if review.get("review_comment") else "",
                "submitted_at": str(review["submitted_at"]) if review.get("submitted_at") else None,
                "created_at": str(review["created_at"]),
            }

        def build_pr_response(pr):
            pr_id = str(pr["pull_request_id"])
            reviews = [
                build_review_response(review)
                for review in pull_request_reviews.values()
                if str(review.get("pull_request_id")) == pr_id
            ]
            reviews.sort(key=lambda r: r.get("created_at", ""))

            return {
                "pull_request_id": pr_id,
                "repository_id": str(pr["repository_id"]),
                "pull_request_number": int(pr["pull_request_number"]),
                "title": str(pr["title"]),
                "description": str(pr.get("description", "")),
                "source_branch_name": str(pr["source_branch_name"]),
                "target_branch_name": str(pr["target_branch_name"]),
                "author_id": str(pr["author_id"]),
                "status": str(pr["status"]),
                "linked_ticket_id": str(pr["linked_ticket_id"]) if pr.get("linked_ticket_id") else None,
                "merged_by": str(pr["merged_by"]) if pr.get("merged_by") else None,
                "merged_at": str(pr["merged_at"]) if pr.get("merged_at") else None,
                "closed_at": str(pr["closed_at"]) if pr.get("closed_at") else None,
                "created_at": str(pr["created_at"]),
                "updated_at": str(pr["updated_at"]),
                "reviews": reviews,
            }

        if pull_request_number is not None and pull_request_id is not None:
            pr = pull_requests.get(str(pull_request_id))
            if not pr:
                return json.dumps(
                    {"error": f"Pull request with ID '{pull_request_id}' not found"}
                )
            if str(pr.get("repository_id")) != repository_id:
                return json.dumps(
                    {"error": f"Pull request '{pull_request_id}' does not belong to repository '{repository_name}'"}
                )
            if pr.get("pull_request_number") != int(pull_request_number):
                return json.dumps(
                    {"error": f"Mismatch: pull_request_id '{pull_request_id}' does not correspond to pull_request_number {int(pull_request_number)}"}
                )
            return json.dumps({"success": True, "pull_request": build_pr_response(pr)})

        if pull_request_id is not None:
            pr = pull_requests.get(str(pull_request_id))
            if not pr:
                return json.dumps(
                    {"error": f"Pull request with ID '{pull_request_id}' not found"}
                )
            if str(pr.get("repository_id")) != repository_id:
                return json.dumps(
                    {"error": f"Pull request '{pull_request_id}' does not belong to repository '{repository_name}'"}
                )
            return json.dumps({"success": True, "pull_request": build_pr_response(pr)})

        pull_request_number = int(pull_request_number)
        for pr in pull_requests.values():
            if (
                pr.get("pull_request_number") == pull_request_number and
                str(pr.get("repository_id")) == repository_id
            ):
                return json.dumps({"success": True, "pull_request": build_pr_response(pr)})

        return json.dumps(
            {"error": f"Pull request with number {pull_request_number} not found in repository '{repository_name}'"}
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_pull_request_details",
                "description": "Fetches the details of a pull request and all the pull request reviews corresponding to the pull request. It should be used when you need to retrieve information about a specific pull request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository",
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "The number of the pull request",
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request",
                        },
                    },
                    "required": ["repository_name"],
                    "anyOf": [
                        {"required": ["pull_request_number"]},
                        {"required": ["pull_request_id"]}
                    ]
                },
            },
        }
