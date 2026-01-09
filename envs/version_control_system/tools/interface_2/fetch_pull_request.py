import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchPullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        pull_request_number: Optional[int] = None,
        title: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """Fetch pull request(s) from a repository based on filters."""

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        pull_requests_dict = data.get("pull_requests", {})
        repositories_dict = data.get("repositories", {})

        # Convert to strings
        repository_id_str = str(repository_id).strip()
        title_str = str(title).strip() if title else None
        status_str = str(status).strip() if status else None

        # Validate repository exists
        if repository_id_str not in repositories_dict:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id_str}' not found",
            })

        # Validate status if provided
        if status_str:
            valid_statuses = ["open", "closed", "merged", "draft"]
            if status_str not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
                })

        # Find matching pull requests
        matching_prs = []
        for pr_id, pr in pull_requests_dict.items():
            if str(pr.get("repository_id")) != repository_id_str:
                continue

            if pull_request_number is not None and int(pr.get("pull_request_number", -1)) != int(pull_request_number):
                continue

            if title_str and str(pr.get("title", "")).strip() != title_str:
                continue

            if status_str and str(pr.get("status", "")).strip() != status_str:
                continue

            # Add matching PR
            pr_copy = pr.copy()
            pr_copy["pull_request_id"] = str(pr_id)
            matching_prs.append(pr_copy)

        # Return results
        if not matching_prs:
            return json.dumps({
                "success": False,
                "error": f"No pull requests found in repository '{repository_id_str}' matching input criteria",
            })

        return json.dumps({
            "success": True,
            "pull_requests": matching_prs,
            "count": len(matching_prs),
            "message": f"Found {len(matching_prs)} pull request(s) in repository '{repository_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the fetch_pull_request function."""
        return {
            "type": "function",
            "function": {
                "name": "fetch_pull_request",
                "description": (
                    "Fetch pull request(s) from a repository based on optional filters. "
                    "Validates that the repository exists. "
                    "If pull_request_number is provided, returns the PR with that exact number. "
                    "If title is provided, returns PR with that exact title. "
                    "If status is provided, returns PR(s) with that status (open/closed/merged/draft). "
                    "Filters can be combined: pull_request_number and title must match the same PR, "
                    "but status can return multiple PRs. "
                    "If no filters are provided, returns all PRs in the repository. "
                    "Returns an array of pull requests with a count field indicating total matches."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository to fetch pull requests from.",
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "Optional. The pull request number to search for (exact match).",
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional. The title to search for (exact match).",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. The status to filter by (open/closed/merged/draft).",
                        },
                    },
                    "required": ["repository_id"],
                },
            },
        }
