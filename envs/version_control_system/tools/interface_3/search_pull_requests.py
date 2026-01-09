import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SearchPullRequests(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        author_id: Optional[str] = None,
        status: Optional[str] = None,
        source_branch: Optional[str] = None,
        target_branch: Optional[str] = None
    ) -> str:
        """
        Searches for pull requests in a repository with optional filters.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to search pull requests"})

        # Validate status if provided
        if status is not None:
            valid_statuses = ["open", "draft", "closed", "merged"]
            if status not in valid_statuses:
                return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: open, draft, closed, merged"})

        repositories = data.get("repositories", {})
        pull_requests = data.get("pull_requests", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Search for pull requests matching the filters
        results = []
        for pr_id, pr in pull_requests.items():
            # Filter by repository_id
            if str(pr.get("repository_id")) != str(repository_id):
                continue

            # Filter by author_id if provided
            if author_id is not None and str(pr.get("author_id")) != str(author_id):
                continue

            # Filter by status if provided
            if status is not None and pr.get("status") != status:
                continue

            # Filter by source_branch if provided
            if source_branch is not None and str(pr.get("source_branch")) != str(source_branch):
                continue

            # Filter by target_branch if provided
            if target_branch is not None and str(pr.get("target_branch")) != str(target_branch):
                continue

            results.append(pr)

        return json.dumps({"success": True, "result": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_pull_requests",
                "description": "Searches for pull requests in a repository with optional filters. Returns a list of pull requests matching the criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to search in."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Filter by the unique identifier of the pull request author. Optional."
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by pull request status. Valid values: open, draft, closed, merged. Optional."
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "Filter by source branch ID. Optional."
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "Filter by target branch ID. Optional."
                        }
                    },
                    "required": ["repository_id"]
                }
            }
        }
